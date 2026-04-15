# Modelo de evidencias

La evidencia no se trata como texto sin contexto. Cada evidencia guarda origen, tipo, hash, metadatos y trazabilidad de storage.

## Campos base

- `id`
- `scope_id`
- `title`
- `source_type`
- `source_name`
- `source_author`
- `evidence_type`
- `mime_type`
- `uploaded_by`
- `storage_path`
- `content_hash`
- `normalized_text`
- `metadata_json`
- `classification`
- `sufficiency_status`
- `freshness_status`

## Tipos soportados

- PDF
- DOCX
- TXT
- CSV
- logs simples
- tickets exportados
- imagenes como referencia documental

## Reglas

- si no hay texto util ni metadatos suficientes, la evidencia queda como insuficiente
- una imagen en esta version se trata como referencia, no como OCR
- la evidencia queda separada de la inferencia y del hallazgo
