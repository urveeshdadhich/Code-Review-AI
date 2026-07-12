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

public class CodeReviewClient {
    private final String provider;
    private final String apiKey;
    private final HttpClient httpClient;
    private final ObjectMapper mapper;

    public CodeReviewClient(String provider, String apiKey) {
        this.provider = provider.toLowerCase();
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
                
        this.mapper = new ObjectMapper()
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true)
                .configure(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES, true);
    }

    public CodeReviewResult reviewCode(String fileContent) throws Exception {
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

        String url;
        String jsonPayload;
        HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                .header("Content-Type", "application/json")
                .timeout(Duration.ofMinutes(2));

        switch (provider) {
            case "openai" -> {
                url = "https://api.openai.com/v1/chat/completions";
                jsonPayload = "{\"model\":\"gpt-4o\",\"response_format\":{\"type\":\"json_object\"},\"messages\":[{\"role\":\"user\",\"content\":" + mapper.writeValueAsString(prompt) + "}]}";
                requestBuilder.header("Authorization", "Bearer " + apiKey);
            }
            case "anthropic" -> {
                url = "https://api.anthropic.com/v1/messages";
                jsonPayload = "{\"model\":\"claude-3-5-sonnet-20241022\",\"max_tokens\":4096,\"messages\":[{\"role\":\"user\",\"content\":" + mapper.writeValueAsString(prompt) + "}]}";
                requestBuilder.header("x-api-key", apiKey);
                requestBuilder.header("anthropic-version", "2023-06-01");
            }
            default -> { // gemini
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + apiKey;
                jsonPayload = "{\"contents\":[{\"parts\":[{\"text\":" + mapper.writeValueAsString(prompt) + "}]}],\"generationConfig\":{\"responseMimeType\":\"application/json\"}}";
            }
        }

        HttpRequest request = requestBuilder
                .uri(URI.create(url))
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException(provider.toUpperCase() + " API Error: " + response.body());
        }

        JsonNode rootNode = mapper.readTree(response.body());
        String rawLlmJson = "";

        switch (provider) {
            case "openai" -> rawLlmJson = rootNode.at("/choices/0/message/content").asText();
            case "anthropic" -> {
                rawLlmJson = rootNode.at("/content/0/text").asText();
                int start = rawLlmJson.indexOf('{');
                int end = rawLlmJson.lastIndexOf('}');
                if (start != -1 && end != -1 && end > start) {
                    rawLlmJson = rawLlmJson.substring(start, end + 1);
                }
            }
            default -> rawLlmJson = rootNode.at("/candidates/0/content/parts/0/text").asText();
        }

        rawLlmJson = rawLlmJson.replaceAll("^```json", "").replaceAll("```$", "").trim();

        return mapper.readValue(rawLlmJson, CodeReviewResult.class);
    }
}
