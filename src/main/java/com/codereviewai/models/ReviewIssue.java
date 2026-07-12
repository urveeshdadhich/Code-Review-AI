package com.codereviewai.models;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ReviewIssue(
    @JsonProperty(value = "file", required = true) 
    String file,
    
    @JsonProperty(value = "line_number", required = true) 
    int lineNumber,
    
    @JsonProperty(value = "severity", required = true) 
    Severity severity,
    
    @JsonProperty(value = "category", required = true) 
    String category,
    
    @JsonProperty(value = "explanation", required = true) 
    String explanation,
    
    @JsonProperty(value = "suggested_fix", required = true) 
    String suggestedFix
) {}
