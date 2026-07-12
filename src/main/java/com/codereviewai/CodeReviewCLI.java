package com.codereviewai;

import com.codereviewai.client.CodeReviewClient;
import com.codereviewai.models.CodeReviewResult;
import com.codereviewai.models.ReviewIssue;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class CodeReviewCLI {

    public static void main(String[] args) {
        String pathStr = null;
        String provider = "gemini";

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--path") && i + 1 < args.length) {
                pathStr = args[++i];
            } else if (args[i].equals("--provider") && i + 1 < args.length) {
                provider = args[++i];
            }
        }

        if (pathStr == null) {
            System.err.println("\u001B[1;31mERROR: --path is required.\u001B[0m");
            System.err.println("Usage: java -jar code-review-ai-1.0.jar --path <path> [--provider <gemini|openai|anthropic>]");
            System.exit(1);
        }

        Path path = Paths.get(pathStr);
        System.out.println("\u001B[1;36mStarting AI Code Review on:\u001B[0m " + path);
        
        String providerKeyName = switch (provider.toLowerCase()) {
            case "openai" -> "OPENAI_API_KEY";
            case "anthropic" -> "ANTHROPIC_API_KEY";
            default -> "GEMINI_API_KEY";
        };

        String apiKey = null;
        if (providerKeyName != null) {
            apiKey = System.getenv(providerKeyName);
            if (apiKey == null || apiKey.isEmpty()) {
                try {
                    java.io.File envFile = new java.io.File(System.getProperty("user.home") + java.io.File.separator + ".code_review_ai.env");
                    if (envFile.exists()) {
                        for (String line : Files.readAllLines(envFile.toPath())) {
                            if (line.startsWith(providerKeyName + "=")) {
                                apiKey = line.split("=", 2)[1].trim();
                            }
                        }
                    }
                } catch (Exception ignored) {}
            }
            if (apiKey == null || apiKey.isEmpty()) {
                System.err.println("\u001B[1;31mERROR: " + providerKeyName + " is not set in environment or ~/.code_review_ai.env.\u001B[0m");
                System.exit(1);
            }
        }

        try {
            String content = Files.readString(path);
            
            CodeReviewClient client = new CodeReviewClient(provider, apiKey);
            
            String providerDisplay = providerKeyName.split("_")[0];
            System.out.println("\u001B[33mAnalyzing codebase using " + providerDisplay + "... Please wait.\u001B[0m\n");
            
            CodeReviewResult result = client.reviewCode(content);

            for (ReviewIssue issue : result.issues()) {
                com.codereviewai.ui.TableFormatter.printIssueTable(issue);
                System.out.println();
            }
            System.out.println("\n\u001B[1;32mSummary:\u001B[0m " + result.summary());

        } catch (Exception e) {
            System.err.println("\u001B[1;31mExecution Failed:\u001B[0m " + e.getMessage());
            System.exit(1);
        }
    }
}
