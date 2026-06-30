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

public class OpenAIClient implements AIClient {
    private final String apiKey;
    private final HttpClient httpClient;
    private final ObjectMapper mapper;

    public OpenAIClient(String apiKey) {
        this.apiKey = apiKey;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
                
        this.mapper = new ObjectMapper()
                .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, true)
                .configure(DeserializationFeature.FAIL_ON_MISSING_CREATOR_PROPERTIES, true);
    }

    @Override
    public List<CodeReviewResult> reviewCode(String fileContent) throws Exception {
        String url = "https://api.openai.com/v1/chat/completions";
        
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

        String jsonPayload = "{\"model\":\"gpt-4o\",\"response_format\":{\"type\":\"json_object\"},\"messages\":[{\"role\":\"user\",\"content\":" + mapper.writeValueAsString(prompt) + "}]}";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + apiKey)
                .timeout(Duration.ofMinutes(2))
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("OpenAI API Error: " + response.body());
        }

        JsonNode rootNode = mapper.readTree(response.body());
        String rawLlmJson = rootNode.at("/choices/0/message/content").asText();
        
        rawLlmJson = rawLlmJson.replaceAll("^```json", "").replaceAll("```$", "").trim();

        CodeReviewResult result = mapper.readValue(rawLlmJson, CodeReviewResult.class);
        return List.of(result);
    }
}
