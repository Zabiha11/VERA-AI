# Important SQL Commands and Examples

## 1. SELECT
Retrieve data from one or more tables.
```sql
SELECT column1, column2
FROM employees
WHERE department = 'Sales'
ORDER BY hire_date DESC;
```

## 2. INSERT
Add new rows to a table.
```sql
INSERT INTO employees (first_name, last_name, department, salary)
VALUES ('Jane', 'Doe', 'Marketing', 62000);
```

## 3. UPDATE
Modify existing rows.
```sql
UPDATE employees
SET salary = salary * 1.05
WHERE performance_rating = 'Excellent';
```

## 4. DELETE
Remove rows from a table.
```sql
DELETE FROM employees
WHERE termination_date < '2023-01-01';
```

## 5. CREATE TABLE
Define a new table structure.
```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    manager_id INT,
    FOREIGN KEY (manager_id) REFERENCES employees(emp_id)
);
```

## 6. ALTER TABLE
Change an existing table.
```sql
-- Add a new column
ALTER TABLE employees ADD COLUMN phone VARCHAR(15);

-- Modify a column datatype
ALTER TABLE employees ALTER COLUMN salary TYPE DECIMAL(10,2);
```

## 7. DROP TABLE
Delete a table permanently.
```sql
DROP TABLE IF EXISTS temp_sales;
```

## 8. JOINs
Combine rows from two or more tables.
```sql
-- INNER JOIN (only matching rows)
SELECT e.first_name, e.last_name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.dept_id;

-- LEFT JOIN (all rows from left table)
SELECT e.first_name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.dept_id;
```

## 9. GROUP BY & HAVING
Aggregate data and filter groups.
```sql
SELECT department, COUNT(*) AS employee_count, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;
```

## 10. ORDER BY
Sort query results.
```sql
SELECT first_name, last_name, hire_date
FROM employees
ORDER BY hire_date ASC, last_name DESC;
```

## 11. LIMIT / OFFSET (or FETCH)
Control result set size.
```sql
-- First 10 rows
SELECT * FROM employees LIMIT 10;

-- Skip first 20 rows, then fetch next 10
SELECT * FROM employees OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

## 12. UNION / UNION ALL
Combine results from multiple SELECT statements.
```sql
SELECT email FROM customers
UNION
SELECT email FROM prospects;  -- removes duplicates

SELECT email FROM customers
UNION ALL
SELECT email FROM prospects;  -- keeps duplicates
```

---
*These examples are written in standard ANSI‑SQL and work in most relational databases (MySQL, PostgreSQL, SQL Server, Oracle, etc.). Adjust data types and functions as needed for a specific system.*