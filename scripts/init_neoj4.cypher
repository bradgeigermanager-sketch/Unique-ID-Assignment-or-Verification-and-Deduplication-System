// 创建索引和约束
CREATE CONSTRAINT employee_id_unique IF NOT EXISTS 
FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE;

CREATE CONSTRAINT dept_id_unique IF NOT EXISTS 
FOR (d:Department) REQUIRE d.dept_id IS UNIQUE;

CREATE INDEX employee_idx IF NOT EXISTS FOR (e:Employee) ON (e.is_active);
CREATE INDEX dept_idx IF NOT EXISTS FOR (d:Department) ON (d.parent_dept_id);

// 创建示例组织数据
CREATE (ceo:Employee {
  employee_id: 'CEO-001',
  name: 'Alice Johnson',
  title: 'CEO',
  department_id: 'DEPT-001',
  hire_date: date('2020-01-01'),
  is_active: true,
  importance_score: 10.0
})

CREATE (cto:Employee {
  employee_id: 'EMP-001',
  name: 'Bob Smith',
  title: 'CTO',
  department_id: 'DEPT-002',
  hire_date: date('2020-03-01'),
  is_active: true,
  importance_score: 9.0
})

CREATE (cfo:Employee {
  employee_id: 'EMP-002',
  name: 'Carol White',
  title: 'CFO',
  department_id: 'DEPT-003',
  hire_date: date('2020-03-01'),
  is_active: true,
  importance_score: 9.0
})

// 创建汇报关系
CREATE (ceo)-[:REPORTS_TO {start_date: date('2020-03-01'), is_active: true}]->(cto)
CREATE (ceo)-[:REPORTS_TO {start_date: date('2020-03-01'), is_active: true}]->(cfo)

// 创建部门
CREATE (dept1:Department {
  dept_id: 'DEPT-001',
  name: 'Executive',
  parent_dept_id: null,
  budget: 10000000
})

CREATE (dept2:Department {
  dept_id: 'DEPT-002',
  name: 'Engineering',
  parent_dept_id: 'DEPT-001',
  budget: 5000000
})

CREATE (dept3:Department {
  dept_id: 'DEPT-003',
  name: 'Finance',
  parent_dept_id: 'DEPT-001',
  budget: 3000000
})

// 创建员工 - 部门关系
MATCH (ceo:Employee {employee_id: 'CEO-001'}), (depts:Department {dept_id: 'DEPT-001'})
CREATE (ceo)-[:WORKS_IN]->(depts)

MATCH (cto:Employee {employee_id: 'EMP-001'}), (depts:Department {dept_id: 'DEPT-002'})
CREATE (cto)-[:WORKS_IN]->(depts)

MATCH (cfo:Employee {employee_id: 'EMP-002'}), (depts:Department {dept_id: 'DEPT-003'})
CREATE (cfo)-[:WORKS_IN]->(depts)

// 创建示例审计日志
CREATE (a1:AuditLog {
  id: randomUUID(),
  action: 'CREATE_EMPLOYEE',
  entity_type: 'Employee',
  entity_id: 'EMP-001',
  user: 'admin',
  details: {reason: 'Initial setup'},
  timestamp: datetime()
})

CREATE (a2:AuditLog {
  id: randomUUID(),
  action: 'CREATE_DEPARTMENT',
  entity_type: 'Department',
  entity_id: 'DEPT-002',
  user: 'admin',
  details: {budget: 5000000},
  timestamp: datetime()
})

RETURN 'Initialization complete' as status;
