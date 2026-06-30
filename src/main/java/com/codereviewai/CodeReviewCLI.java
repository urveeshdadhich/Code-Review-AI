package com.codereviewai;
import com.codereviewai.client.AIClient;
import com.codereviewai.client.AnthropicClient;
import com.codereviewai.client.GeminiClient;
import com.codereviewai.client.OpenAIClient;
import com.codereviewai.client.OllamaClient;
import com.codereviewai.models.CodeReviewResult;
import com.codereviewai.models.ReviewIssue;
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.Callable;

@Command(name = "cr", mixinStandardHelpOptions = true, version = "1.0",
         description = "AI-Powered Code Review CLI Tool")
public class CodeReviewCLI implements Callable<Integer> {

    @Option(names = {"--path"}, description = "Local file or directory path to review.", required = false)
    private Path path;
    
    @Option(names = {"--provider"}, description = "AI Provider to use: gemini, openai, anthropic, ollama. Default is gemini.", required = false)
    private String provider = "gemini";

    @Override
    public Integer call() {
        if (path == null) {
            new TUI().start();
            System.exit(0);
            return 0;
        }

        System.out.println(CommandLine.Help.Ansi.AUTO.string("@|bold,cyan Starting AI Code Review on:|@ " + path));
        
        String providerKeyName = switch (provider.toLowerCase()) {
            case "openai" -> "OPENAI_API_KEY";
            case "anthropic" -> "ANTHROPIC_API_KEY";
            case "ollama" -> null;
            default -> "GEMINI_API_KEY";
        };

        String apiKey = null;
        if (providerKeyName != null) {
            apiKey = System.getenv(providerKeyName);
            if (apiKey == null || apiKey.isEmpty()) {
                System.err.println(CommandLine.Help.Ansi.AUTO.string("@|bold,red ERROR: " + providerKeyName + " environment variable is not set.|@"));
                return 1;
            }
        }

        try {
            String content = Files.readString(path);
            
            AIClient client = switch (provider.toLowerCase()) {
                case "openai" -> new OpenAIClient(apiKey);
                case "anthropic" -> new AnthropicClient(apiKey);
                case "ollama" -> new OllamaClient();
                default -> new GeminiClient(apiKey);
            };
            
            String providerDisplay = providerKeyName != null ? providerKeyName.split("_")[0] : "Ollama (Local)";
            System.out.println(CommandLine.Help.Ansi.AUTO.string("@|yellow Analyzing codebase using " + providerDisplay + "... Please wait.|@\n"));
            
            List<CodeReviewResult> results = client.reviewCode(content);

            for (CodeReviewResult result : results) {
                for (ReviewIssue issue : result.issues()) {
                    com.codereviewai.ui.TableFormatter.printIssueTable(issue);
                    System.out.println();
                }
                System.out.println(CommandLine.Help.Ansi.AUTO.string("\n@|bold,green Summary:|@ " + result.summary()));
            }

        } catch (Exception e) {
            System.err.println(CommandLine.Help.Ansi.AUTO.string("@|bold,red Execution Failed:|@ " + e.getMessage()));
            return 1;
        }
        return 0;
    }

    public static void main(String[] args) {
        int exitCode = new CommandLine(new CodeReviewCLI()).execute(args);
        System.exit(exitCode);
    }
}
