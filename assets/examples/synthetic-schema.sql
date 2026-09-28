CREATE TABLE PARTY (party_id VARCHAR(32) PRIMARY KEY, id_namespace VARCHAR(40), name VARCHAR(100));
CREATE TABLE PRODUCT (product_code VARCHAR(24) PRIMARY KEY, name VARCHAR(100));
CREATE TABLE AGREEMENT (agreement_id VARCHAR(32) PRIMARY KEY, product_code VARCHAR(24), FOREIGN KEY(product_code) REFERENCES PRODUCT(product_code));
CREATE TABLE ACCT (account_id VARCHAR(32) PRIMARY KEY, party_id VARCHAR(32), balance DECIMAL(20,2), currency VARCHAR(3), as_of_date DATE, FOREIGN KEY(party_id) REFERENCES PARTY(party_id));
CREATE TABLE PAYMENT_INSTRUCTION (instruction_id VARCHAR(32) PRIMARY KEY, debit_account VARCHAR(32), credit_reference VARCHAR(80), amount DECIMAL(20,2), status VARCHAR(12), FOREIGN KEY(debit_account) REFERENCES ACCT(account_id));
CREATE TABLE POSITION_OBSERVATION (account_id VARCHAR(32), instrument_id VARCHAR(32), observed_at TIMESTAMP, quantity DECIMAL(24,8), PRIMARY KEY(account_id,instrument_id,observed_at));
COMMENT ON COLUMN ACCT.balance IS '余额口径尚待业务确认';
