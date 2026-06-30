package com.codereviewai.client;

import com.codereviewai.models.CodeReviewResult;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;

public class OllamaClient implements AIClient {
    private final HttpClient httpClient;
    private final ObjectMapper mapper;
    private final String model = "llama3.2";
    private boolean modelEnsured = false;

    public OllamaClient() {
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
                
        this.mapper = new ObjectMapper()
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true)
                .configure(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES, true);
    }

    private synchronized void ensureModel() {
        if (modelEnsured) return;
        
        try {
            Process versionProc = new ProcessBuilder("ollama", "--version").start();
            if (versionProc.waitFor() != 0) {
                throw new RuntimeException("Ollama executable not found. Please install Ollama from https://ollama.com");
            }

            Process listProc = new ProcessBuilder("ollama", "list").start();
            int listCode = listProc.waitFor();
            String listOutput = new String(listProc.getInputStream().readAllBytes());
            String listError = new String(listProc.getErrorStream().readAllBytes());

            if (listCode != 0 || listError.toLowerCase().contains("could not connect") || listError.toLowerCase().contains("is it running") || listError.toLowerCase().contains("connection refused")) {
                System.out.println("\u001B[33mOllama server is not running. Starting it in the background...\u001B[0m");
                new ProcessBuilder("ollama", "serve").start();
                Thread.sleep(3000);
                
                Process listRetry = new ProcessBuilder("ollama", "list").start();
                listRetry.waitFor();
                listOutput = new String(listRetry.getInputStream().readAllBytes());
            }

            if (!listOutput.contains(model)) {
                System.out.println("\n\u001B[33mModel '" + model + "' not found locally. Downloading now... (This may take a few minutes)\u001B[0m");
                Process pullProc = new ProcessBuilder("ollama", "pull", model).inheritIO().start();
                pullProc.waitFor();
                System.out.println("\u001B[32mSuccessfully downloaded '" + model + "'!\u001B[0m\n");
            }
            
            modelEnsured = true;
        } catch (Exception e) {
            System.err.println("\u001B[31mFailed to check or pull ollama model: " + e.getMessage() + "\u001B[0m");
        }
    }

    @Override
    public List<CodeReviewResult> reviewCode(String fileContent) throws Exception {
        ensureModel();
        
        String url = "http://localhost:11434/api/chat";
        
        String prompt = "You are a Principal Staff Engineer. Review the provided code for bugs, vulnerabilities, and logic errors.\n" +
                        "CRITICAL: Output ONLY valid JSON. Do not include markdown formatting or explanation outside the JSON.\n" +
                        "The JSON MUST follow this exact structure:\n" +
                        "{\n" +
                        "  \"issues\": [\n" +
                        "    {\n" +
                        "      \"file\": \"<filename>\",\n" +
                        "      \"line_number\": <integer>,\n" +
                        "      \"severity\": \"HIGH\" (or \"MEDIUM\" or \"LOW\"),\n" +
                        "      \"category\": \"<e.g. Bug, Security, Performance>\",\n" +
                        "      \"explanation\": \"<description>\",\n" +
                        "      \"suggested_fix\": \"<markdown code block with ```>\"\n" +
                        "    }\n" +
                        "  ],\n" +
                        "  \"summary\": \"<overall summary>\"\n" +
                        "}\n\n" +
                        "Code to review:\n" + fileContent;

        String jsonPayload = "{\"model\":\"" + model + "\",\"format\":\"json\",\"stream\":false,\"options\":{\"num_predict\":8192},\"messages\":[{\"role\":\"user\",\"content\":" + mapper.writeValueAsString(prompt) + "}]}";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofMinutes(10))
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("Ollama API Error: " + response.body());
        }

        JsonNode rootNode = mapper.readTree(response.body());
        String rawLlmJson = rootNode.at("/message/content").asText();
        
        int start = rawLlmJson.indexOf('{');
        int end = rawLlmJson.lastIndexOf('}');
        if (start != -1 && end != -1 && end > start) {
            rawLlmJson = rawLlmJson.substring(start, end + 1);
        }

        CodeReviewResult result = mapper.readValue(rawLlmJson, CodeReviewResult.class);
        return List.of(result);
    }
}
