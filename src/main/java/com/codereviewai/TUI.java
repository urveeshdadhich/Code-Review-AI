package com.codereviewai;

import org.jline.reader.LineReader;
import org.jline.reader.LineReaderBuilder;
import org.jline.reader.UserInterruptException;
import org.jline.reader.EndOfFileException;
import org.jline.reader.impl.completer.FileNameCompleter;
import org.jline.terminal.Attributes;
import org.jline.terminal.Terminal;
import org.jline.terminal.TerminalBuilder;
import org.jline.utils.NonBlockingReader;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class TUI {
    private final String envPath = System.getProperty("user.home") + File.separator + ".code_review_ai.env";
    private Terminal terminal;
    private LineReader generalReader;
    private LineReader fileReader;

    public TUI() {
        try {
            // Preload class to prevent JVM shutdown hook NoClassDefFoundError on Ctrl+C
            Class.forName("org.jline.terminal.Terminal$MouseTracking");
            Class.forName("org.jline.terminal.Terminal$Signal");
            Class.forName("org.jline.terminal.Terminal$SignalHandler");
        } catch (ClassNotFoundException ignored) {}

        try {
            terminal = TerminalBuilder.builder().system(true).build();
            generalReader = LineReaderBuilder.builder().terminal(terminal).build();
            fileReader = LineReaderBuilder.builder()
                            .terminal(terminal)
                            .completer(new FileNameCompleter())
                            .build();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void start() {
        try {
            while (true) {
                String[] options = {"Run Code Review", "Configure API Keys", "Exit"};
                int choice = selectMenu("? What would you like to do?", options);
                
                if (choice == 2) {
                    System.out.println("Goodbye!");
                    break;
                } else if (choice == 1) {
                    configureKeys();
                } else if (choice == 0) {
                    runReview();
                }
            }
        } catch (UserInterruptException | EndOfFileException e) {
            System.out.println("\nExiting CodeReviewAI. Goodbye!");
            System.exit(0);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private int selectMenu(String title, String[] options) throws IOException {
        Attributes prev = terminal.enterRawMode();
        NonBlockingReader reader = terminal.reader();
        
        int selected = 0;
        try {
            while (true) {
                System.out.print("\033[H\033[2J");
                System.out.flush();
                System.out.println("\r\n\u001B[36m\u001B[1m" + title + "\u001B[0m\r\n");
                
                for (int i = 0; i < options.length; i++) {
                    if (i == selected) {
                        System.out.println("\u001B[36m  > " + options[i] + "\u001B[0m\r");
                    } else {
                        System.out.println("    " + options[i] + "\r");
                    }
                }
                
                int c = reader.read();
                if (c == 27) { // ESC sequence
                    int next = reader.read();
                    if (next == 91) { // '['
                        int arrow = reader.read();
                        if (arrow == 65) { // UP
                            selected = (selected > 0) ? selected - 1 : options.length - 1;
                        } else if (arrow == 66) { // DOWN
                            selected = (selected < options.length - 1) ? selected + 1 : 0;
                        }
                    }
                } else if (c == 13 || c == 10) { // Enter
                    break;
                } else if (c == 3) { // Ctrl+C
                    terminal.setAttributes(prev);
                    System.exit(0);
                }
            }
        } finally {
            terminal.setAttributes(prev);
        }
        
        System.out.print("\033[H\033[2J");
        System.out.flush();
        return selected;
    }

    private void configureKeys() throws IOException {
        String[] options = {"GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "Cancel"};
        int choice = selectMenu("? Which provider's API key do you want to configure?", options);
        
        if (choice == 3) return;
        
        String provider = options[choice];
        String key = generalReader.readLine("Enter new " + provider + " (leave blank to cancel): ").trim();
        
        if (!key.isEmpty()) {
            saveEnvVar(provider, key);
            System.out.println("\u001B[32mSuccessfully saved " + provider + " globally.\u001B[0m\n");
            try { Thread.sleep(1500); } catch (Exception e) {}
        }
    }

    private void saveEnvVar(String key, String value) {
        try {
            File f = new File(envPath);
            List<String> lines = new ArrayList<>();
            if (f.exists()) {
                lines = Files.readAllLines(f.toPath());
            }
            boolean found = false;
            for (int i = 0; i < lines.size(); i++) {
                if (lines.get(i).startsWith(key + "=")) {
                    lines.set(i, key + "=" + value);
                    found = true;
                }
            }
            if (!found) {
                lines.add(key + "=" + value);
            }
            Files.write(f.toPath(), lines);
        } catch (IOException e) {
            System.out.println("Error saving key: " + e.getMessage());
        }
    }

    private void runReview() throws IOException {
        String[] providers = {"Google Gemini", "OpenAI (ChatGPT)", "Anthropic (Claude)", "Ollama (Local)"};
        int providerChoice = selectMenu("? Select AI Provider for this review:", providers);
        
        String providerKeyName = switch (providerChoice) {
            case 1 -> "OPENAI_API_KEY";
            case 2 -> "ANTHROPIC_API_KEY";
            case 3 -> null;
            default -> "GEMINI_API_KEY";
        };

        String path = promptPath("? Enter file or directory path to review (default: .): ");
        if (path.isEmpty()) path = ".";

        System.out.println("\n\u001B[34mAnalyzing codebase... Please wait.\u001B[0m\n");
        String apiKey = null;
        if (providerKeyName != null) {
            apiKey = System.getenv(providerKeyName);
            if (apiKey == null || apiKey.isEmpty()) {
                try {
                    File f = new File(envPath);
                    if (f.exists()) {
                        for (String line : Files.readAllLines(f.toPath())) {
                            if (line.startsWith(providerKeyName + "=")) {
                                apiKey = line.split("=", 2)[1].trim();
                            }
                        }
                    }
                } catch (Exception e) {}
            }
            
            if (apiKey == null || apiKey.isEmpty()) {
                System.out.println("\u001B[31mError: " + providerKeyName + " is not configured.\u001B[0m");
                try {
                    generalReader.readLine("\nPress Enter to return to main menu...");
                } catch (Exception e) {}
                return;
            }
        }

        try {
            String content = Files.readString(Paths.get(path));
            
            com.codereviewai.client.AIClient client = switch (providerChoice) {
                case 1 -> new com.codereviewai.client.OpenAIClient(apiKey);
                case 2 -> new com.codereviewai.client.AnthropicClient(apiKey);
                case 3 -> new com.codereviewai.client.OllamaClient();
                default -> new com.codereviewai.client.GeminiClient(apiKey);
            };
            
            var results = client.reviewCode(content);

            for (var result : results) {
                for (var issue : result.issues()) {
                    com.codereviewai.ui.TableFormatter.printIssueTable(issue);
                    System.out.println();
                }
                System.out.println("\n\u001B[1;32mSummary:\u001B[0m " + result.summary());
            }
        } catch (UserInterruptException | EndOfFileException e) {
            System.out.println("\nExiting CodeReviewAI. Goodbye!");
            System.exit(0);
        } catch (Exception e) {
            System.out.println("Execution Failed: " + e.getMessage());
        }
        
        try {
            generalReader.readLine("\nPress Enter to return to main menu...");
        } catch (UserInterruptException | EndOfFileException e) {
            System.out.println("\nExiting CodeReviewAI. Goodbye!");
            System.exit(0);
        }
    }

    private String promptPath(String title) throws IOException {
        Attributes prev = terminal.enterRawMode();
        NonBlockingReader reader = terminal.reader();
        
        StringBuilder buffer = new StringBuilder("");
        int selected = 0;
        List<String> suggestions = getFileSuggestions(buffer.toString());
        
        try {
            while (true) {
                System.out.print("\033[H\033[2J");
                System.out.flush();
                System.out.println("\r\n\u001B[36m\u001B[1m" + title + "\u001B[0m\r\n");
                System.out.println("  > " + buffer.toString() + "\u001B[5m_\u001B[25m\r\n");
                
                int maxSuggestions = Math.min(10, suggestions.size());
                for (int i = 0; i < maxSuggestions; i++) {
                    if (i == selected) {
                        System.out.println("\u001B[32m    > " + suggestions.get(i) + "\u001B[0m\r");
                    } else {
                        System.out.println("      " + suggestions.get(i) + "\r");
                    }
                }
                
                int c = reader.read();
                if (c == 27) { // ESC sequence
                    int next = reader.read(10);
                    if (next == 91) { // '['
                        int arrow = reader.read(10);
                        if (arrow == 65) { // UP
                            selected = (selected > 0) ? selected - 1 : maxSuggestions - 1;
                        } else if (arrow == 66) { // DOWN
                            selected = (selected < maxSuggestions - 1) ? selected + 1 : 0;
                        } else if (arrow == 67) { // RIGHT
                            if (!suggestions.isEmpty()) {
                                buffer = new StringBuilder(suggestions.get(selected));
                                if (new File(buffer.toString()).isDirectory() && !buffer.toString().endsWith(File.separator)) {
                                    buffer.append(File.separator);
                                }
                                suggestions = getFileSuggestions(buffer.toString());
                                selected = 0;
                            }
                        }
                    }
                } else if (c == 9) { // TAB
                    if (!suggestions.isEmpty()) {
                        buffer = new StringBuilder(suggestions.get(selected));
                        if (new File(buffer.toString()).isDirectory() && !buffer.toString().endsWith(File.separator)) {
                            buffer.append(File.separator);
                        }
                        suggestions = getFileSuggestions(buffer.toString());
                        selected = 0;
                    }
                } else if (c == 127 || c == 8) { // Backspace
                    if (buffer.length() > 0) {
                        buffer.deleteCharAt(buffer.length() - 1);
                        suggestions = getFileSuggestions(buffer.toString());
                        selected = 0;
                    }
                } else if (c == 13 || c == 10) { // Enter
                    if (!suggestions.isEmpty()) {
                        return suggestions.get(selected);
                    }
                    return buffer.toString().isEmpty() ? "." : buffer.toString();
                } else if (c == 3) { // Ctrl+C
                    terminal.setAttributes(prev);
                    System.exit(0);
                } else if (c >= 32 && c <= 126) { // Typable character
                    buffer.append((char) c);
                    suggestions = getFileSuggestions(buffer.toString());
                    selected = 0;
                }
            }
        } finally {
            terminal.setAttributes(prev);
            System.out.print("\033[H\033[2J");
            System.out.flush();
        }
    }

    private List<String> getFileSuggestions(String input) {
        List<String> results = new ArrayList<>();
        String pathStr = input.isEmpty() ? "." : input;
        File file = new File(pathStr);
        
        File dir;
        String prefix;
        if (file.isDirectory() && (input.endsWith(File.separator) || input.isEmpty() || input.equals("."))) {
            dir = file;
            prefix = "";
        } else {
            dir = file.getParentFile();
            if (dir == null) dir = new File(".");
            prefix = file.getName();
        }
        
        File[] files = dir.listFiles();
        if (files != null) {
            for (File f : files) {
                if (f.getName().startsWith(".") && !prefix.startsWith(".")) {
                    if (!input.isEmpty() && !input.equals(".")) continue; 
                }
                
                if (f.getName().startsWith(prefix)) {
                    String relPath = f.getPath();
                    if (relPath.startsWith("." + File.separator)) {
                        relPath = relPath.substring(2);
                    }
                    
                    if (f.isDirectory()) {
                        results.add(relPath + File.separator);
                    } else {
                        String name = f.getName().toLowerCase();
                        if (name.endsWith(".java") || name.endsWith(".py") || name.endsWith(".js") || name.endsWith(".ts") 
                            || name.endsWith(".cpp") || name.endsWith(".c") || name.endsWith(".h") || name.endsWith(".go") 
                            || name.endsWith(".rs") || name.endsWith(".md") || name.endsWith(".json")) {
                            results.add(relPath);
                        }
                    }
                }
            }
        }
        Collections.sort(results);
        return results;
    }
}
