import java.util.Scanner;

public class App {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter user ID: ");
        
        // Missing input validation for integer parsing
        String input = scanner.nextLine();
        int userId = Integer.parseInt(input); 
        
        // Security Vulnerability: SQL Injection
        String query = "SELECT * FROM users WHERE id = " + userId;
        System.out.println("Executing: " + query);
        
        // Logic Error: NullPointerException risk
        String role = null;
        if (userId == 1) {
            role = "Admin";
        }
        
        if (role.equals("Admin")) { // Will crash if userId != 1
            System.out.println("Access Granted");
        }
    }
}
