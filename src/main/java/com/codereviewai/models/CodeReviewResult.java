package com.codereviewai.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record CodeReviewResult(
    @JsonProperty(value = "issues", required = true) 
    List<ReviewIssue> issues,
    
    @JsonProperty(value = "summary", required = true) 
    String summary
) {}
