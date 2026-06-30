package com.codereviewai.client;

import com.codereviewai.models.CodeReviewResult;
import java.util.List;

public interface AIClient {
    List<CodeReviewResult> reviewCode(String fileContent) throws Exception;
}
