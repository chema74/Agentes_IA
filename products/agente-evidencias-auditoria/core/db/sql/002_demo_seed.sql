INSERT INTO audit_scopes (id, name, description, framework, status, created_by)
VALUES ('ISO27001-demo', 'ISO27001-demo', 'Scope demo para trazabilidad de evidencias y controles.', 'ISO 27001', 'in_review', 'demo-compliance');

INSERT INTO controls (id, scope_id, code, name, description, category, criticality, expected_criterion, status, owner_user_id)
VALUES
('control-access-001', 'ISO27001-demo', 'A.5.15', 'Revision periodica de accesos privilegiados', 'Revision y aprobacion periodica de accesos privilegiados.', 'access_management', 'high', 'Debe existir owner, procedimiento y evidencia de revision.', 'active', 'demo-owner'),
('control-logging-002', 'ISO27001-demo', 'A.8.15', 'Monitorizacion y conservacion de logs', 'Conservacion y monitorizacion de logs de seguridad.', 'logging', 'medium', 'Debe existir export de logs y seguimiento.', 'active', NULL),
('control-ticketing-003', 'ISO27001-demo', 'OPS-12', 'Seguimiento de incidencias criticas', 'Las incidencias criticas deben quedar registradas y remediadas.', 'incident_management', 'critical', 'Debe existir ticket, owner y remediacion.', 'active', 'demo-owner');

INSERT INTO user_role_assignments (id, scope_id, user_id, role)
VALUES
('ura-001', 'ISO27001-demo', 'demo-compliance', 'compliance'),
('ura-002', 'ISO27001-demo', 'demo-auditor', 'auditor'),
('ura-003', 'ISO27001-demo', 'demo-owner', 'owner');
