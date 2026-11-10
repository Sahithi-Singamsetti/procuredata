
CREATE TABLE IF NOT EXISTS spend_transactions (

    contract_transaction_unique_key TEXT PRIMARY KEY,

    award_id_piid TEXT NOT NULL,

    federal_action_obligation NUMERIC(20, 2) NOT NULL,

    action_date DATE NOT NULL,

    recipient_uei TEXT NOT NULL,

    recipient_name TEXT NOT NULL,

    product_or_service_code TEXT,

    product_or_service_code_description TEXT,

    naics_code TEXT,

    naics_description TEXT

);