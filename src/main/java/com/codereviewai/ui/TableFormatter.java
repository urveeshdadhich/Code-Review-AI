package com.codereviewai.ui;

import com.codereviewai.models.ReviewIssue;
import java.util.ArrayList;
import java.util.List;

public class TableFormatter {


    public static void printIssueTable(ReviewIssue issue) {
        int leftWidth = 10;
        int rightWidth = 87;

        String sep = "├" + "─".repeat(leftWidth + 2) + "┼" + "─".repeat(rightWidth + 2) + "┤";

        System.out.println("┌" + "─".repeat(leftWidth + 2) + "┬" + "─".repeat(rightWidth + 2) + "┐");
        
        printRow("Severity", formatSeverity(issue.severity()), leftWidth, rightWidth, true);
        System.out.println(sep);
        
        printRow("File", "\u001B[35m" + issue.file() + " : " + issue.lineNumber() + "\u001B[0m", leftWidth, rightWidth, true);
        System.out.println(sep);
        
        printRow("Category", issue.category(), leftWidth, rightWidth, true);
        System.out.println(sep);
        
        printRow("Issue", issue.explanation(), leftWidth, rightWidth, false);
        System.out.println(sep);
        
        printRow("Fix", issue.suggestedFix(), leftWidth, rightWidth, false);
        
        System.out.println("└" + "─".repeat(leftWidth + 2) + "┴" + "─".repeat(rightWidth + 2) + "┘");
    }

    private static String formatSeverity(com.codereviewai.models.Severity sev) {
        return switch (sev) {
            case HIGH -> "\u001B[31mHIGH\u001B[0m";
            case MEDIUM -> "\u001B[33mMEDIUM\u001B[0m";
            case LOW -> "\u001B[34mLOW\u001B[0m";
        };
    }

    private static void printRow(String key, String value, int leftWidth, int rightWidth, boolean isSingleLine) {
        List<String> rightLines;
        if (key.equals("Fix")) {
            rightLines = formatFix(value, rightWidth);
        } else if (isSingleLine) {
            rightLines = List.of(value);
        } else {
            rightLines = wordWrap(value, rightWidth);
        }

        for (int i = 0; i < rightLines.size(); i++) {
            String left = (i == 0) ? key : "";
            System.out.printf("│ %s │ %s │\n", pad(left, leftWidth), pad(rightLines.get(i), rightWidth));
        }
    }

    private static String pad(String text, int width) {
        int visibleLen = text.replaceAll("\u001B\\[[;\\d]*m", "").length();
        int padding = Math.max(0, width - visibleLen);
        return text + " ".repeat(padding);
    }

    private static List<String> formatFix(String content, int width) {
        List<String> result = new ArrayList<>();
        String[] blocks = content.split("```");
        for (int i = 0; i < blocks.length; i++) {
            if (i % 2 == 1) { // Code block
                String code = blocks[i];
                code = code.replace("\r", ""); // Destroy carriage returns that break terminal borders
                code = code.replaceFirst("^[a-zA-Z0-9_+-]*\n", ""); // Remove markdown language tag
                code = code.replaceFirst("\\s+$", ""); // Remove ONLY trailing whitespace, preserve leading!
                code = code.replace("\t", "    ");
                
                String[] codeLines = code.split("\n");
                for (String cLine : codeLines) {
                    if (cLine.isEmpty()) {
                        result.add("");
                        continue;
                    }
                    while (cLine.length() > width - 2) {
                        String chunk = "  " + cLine.substring(0, width - 2);
                        result.add(highlightSyntax(chunk));
                        cLine = cLine.substring(width - 2);
                    }
                    if (!cLine.isEmpty()) {
                        result.add(highlightSyntax("  " + cLine));
                    }
                }
            } else { // Text
                if (blocks[i].trim().isEmpty()) continue;
                String textBlock = blocks[i].replace("\r", "");
                result.addAll(wordWrap(textBlock.trim(), width));
            }
        }
        return result;
    }

    private static String highlightSyntax(String code) {
        code = code.replaceAll("\\b(public|private|protected|class|interface|record|extends|implements|return|if|else|for|while|new|static|final|void|int|String|boolean|var|const|let|function|def|using|namespace)\\b", "\u001B[35m$1\u001B[0m");
        code = code.replaceAll("\\b(null|true|false)\\b", "\u001B[33m$1\u001B[0m");
        code = code.replaceAll("(\"[^\"]*\")", "\u001B[32m$1\u001B[0m");
        code = code.replaceAll("([{}()])", "\u001B[36m$1\u001B[0m");
        return code;
    }

    private static List<String> wordWrap(String text, int width) {
        List<String> lines = new ArrayList<>();
        for (String paragraph : text.split("\n")) {
            if (paragraph.trim().isEmpty()) {
                lines.add("");
                continue;
            }
            while (paragraph.length() > width) {
                int space = paragraph.lastIndexOf(' ', width);
                if (space == -1) {
                    lines.add(paragraph.substring(0, width));
                    paragraph = paragraph.substring(width);
                } else {
                    lines.add(paragraph.substring(0, space));
                    paragraph = paragraph.substring(space + 1);
                }
            }
            if (!paragraph.isEmpty()) {
                lines.add(paragraph);
            }
        }
        return lines;
    }
}
