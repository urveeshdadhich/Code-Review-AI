import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class Sample {
    public void getUser(String username) {
        try {
            // hardcoded credentials
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/test", "root", "password");
            Statement stmt = conn.createStatement();
            
            // security vulnerability: sql injection
            String query = "SELECT * FROM users WHERE username = '" + username + "'";
            ResultSet rs = stmt.executeQuery(query);
            
            while(rs.next()) {
                System.out.println(rs.getString("username"));
            }
        } catch (Exception e) {
            // bad practice: weak exception handling
            e.printStackTrace();
        }
    }
}
