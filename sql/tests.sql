-- Load CSVs into tables
CREATE OR REPLACE TABLE deployments AS
SELECT * FROM read_csv_auto('data/deployments.csv');

CREATE OR REPLACE TABLE change_tickets AS
SELECT * FROM read_csv_auto('data/change_tickets.csv');

-- Exception 1: Prod deployment missing a ticket
CREATE OR REPLACE VIEW ex_missing_ticket AS
SELECT
  d.*, 'MISSING_TICKET' AS exception_type
FROM deployments d
WHERE d.environment = 'prod' AND d.ticket_id IS NULL;

-- Exception 2: Ticket missing approval (approved_at null)
CREATE OR REPLACE VIEW ex_missing_approval AS
SELECT
  d.*, 'MISSING_APPROVAL' AS exception_type
FROM deployments d
JOIN change_tickets t ON d.ticket_id = t.ticket_id
WHERE d.environment = 'prod' AND t.approved_at IS NULL;

-- Exception 3: Approval occurs after deployment
CREATE OR REPLACE VIEW ex_approval_after_deploy AS
SELECT
  d.*, 'APPROVAL_AFTER_DEPLOY' AS exception_type
FROM deployments d
JOIN change_tickets t ON d.ticket_id = t.ticket_id
WHERE d.environment = 'prod'
  AND t.approved_at IS NOT NULL
  AND CAST(t.approved_at AS TIMESTAMP) > CAST(d.deployed_at AS TIMESTAMP);

-- Exception 4: Ticket status not approved but deployed
CREATE OR REPLACE VIEW ex_not_approved_status AS
SELECT
  d.*, 'TICKET_NOT_APPROVED' AS exception_type
FROM deployments d
JOIN change_tickets t ON d.ticket_id = t.ticket_id
WHERE d.environment = 'prod'
  AND lower(CAST(t.status AS VARCHAR)) <> 'approved';

-- Exception 5: Missing testing evidence
CREATE OR REPLACE VIEW ex_missing_testing_evidence AS
SELECT
  d.*, 'MISSING_TESTING_EVIDENCE' AS exception_type
FROM deployments d
JOIN change_tickets t ON d.ticket_id = t.ticket_id
WHERE d.environment = 'prod'
  AND lower(CAST(t.testing_evidence AS VARCHAR)) <> 'yes';

-- Combine all exceptions
CREATE OR REPLACE VIEW all_exceptions AS
SELECT * FROM ex_missing_ticket
UNION ALL
SELECT * FROM ex_missing_approval
UNION ALL
SELECT * FROM ex_approval_after_deploy
UNION ALL
SELECT * FROM ex_not_approved_status
UNION ALL
SELECT * FROM ex_missing_testing_evidence;

-- Summary metrics
CREATE OR REPLACE VIEW summary AS
SELECT
  COUNT(*) FILTER (WHERE environment='prod') AS prod_deployments,
  COUNT(*) AS total_deployments
FROM deployments;

CREATE OR REPLACE VIEW exceptions_by_type AS
SELECT exception_type, COUNT(*) AS exception_count
FROM all_exceptions
GROUP BY 1
ORDER BY 2 DESC;

CREATE OR REPLACE VIEW exceptions_by_service AS
SELECT service, COUNT(*) AS exception_count
FROM all_exceptions
GROUP BY 1
ORDER BY 2 DESC;