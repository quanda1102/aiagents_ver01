import mysql.connector
from mysql.connector import Error
from my_agents.config import config

class DatabaseTool:
    def __init__(self):
        db_config = config["databaseClients"]["mysql"]
        self.host = db_config["host"]
        self.port = db_config["port"]
        self.user = db_config["user"]
        self.password = db_config["password"]
        self.database = db_config["database"]
        self.connection = None

    def _connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
            except Error as e:
                print(f"Error while connecting to MySQL: {e}")
                raise

    def _disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def get_schema(self) -> str:
        self._connect()
        cursor = self.connection.cursor(dictionary=True)
        schema_str = ""
        
        try:
            cursor.execute("SHOW TABLES")
            tables = [row[f'Tables_in_{self.database}'] for row in cursor.fetchall()]
            
            for table_name in tables:
                schema_str += f"Table: {table_name}\n"
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for column in columns:
                    schema_str += f"  - {column['Field']} ({column['Type']})\n"
                schema_str += "\n"
        
        except Error as e:
            print(f"Error getting schema: {e}")
            raise
        finally:
            cursor.close()
            self._disconnect()
            
        return schema_str.strip()

    def validate_sql(self, sql: str) -> dict:
        if not sql.strip():
            return {"valid": False, "message": "SQL query is empty."}
            
        self._connect()
        cursor = self.connection.cursor()
        result = {}
        
        try:
            # Using EXPLAIN to validate the query without executing it
            cursor.execute(f"EXPLAIN {sql}")
            cursor.fetchall() # Consume the result of EXPLAIN
            result = {"valid": True, "message": "SQL syntax appears to be valid."}
            
        except Error as e:
            result = {"valid": False, "message": f"SQL Error: {e.args[0]}"}
        finally:
            cursor.close()
            self._disconnect()
            
        return result

    def execute_sql(self, sql: str) -> dict:
        if not sql.strip():
            return {"error": "SQL query is empty."}

        validation = self.validate_sql(sql)
        if not validation["valid"]:
            return {"error": f"Validation failed: {validation['message']}"}

        self._connect()
        # Use a dictionary cursor to get results as key-value pairs
        cursor = self.connection.cursor(dictionary=True)
        result = {}

        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            result = {"data": data, "row_count": cursor.rowcount}

        except Error as e:
            result = {"error": f"SQL Execution Error: {e.args[0]}"}
        finally:
            cursor.close()
            self._disconnect()

        return result

if __name__ == '__main__':
    # This is for testing the tool directly
    # You need to have a .env file in the backend directory with DB credentials
    try:
        tool = DatabaseTool()
        
        print("--- Getting Schema ---")
        schema = tool.get_schema()
        print(schema)
        
        print("\n--- Validating SQL (Valid) ---")
        valid_sql = "SELECT * FROM users;"
        validation_result = tool.validate_sql(valid_sql)
        print(validation_result)

        print("\n--- Validating SQL (Invalid) ---")
        invalid_sql = "SELECT foobar FROM non_existent_table;"
        validation_result = tool.validate_sql(invalid_sql)
        print(validation_result)

    except Exception as main_exc:
        print(f"An error occurred: {main_exc}")
