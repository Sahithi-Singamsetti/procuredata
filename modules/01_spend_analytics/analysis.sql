
-- 1. Calculate total net procurement spend

SELECT
    SUM(federal_action_obligation) AS total_net_spend
FROM spend_transactions;

-- 2. Calculate monthly net procurement spend

SELECT
    DATE_TRUNC('month', action_date) AS spending_month,
    SUM(federal_action_obligation) AS monthly_net_spend
FROM spend_transactions
GROUP BY DATE_TRUNC('month', action_date)
ORDER BY spending_month;

--3. Find the top 10 suppliers by net obligations

SELECT
    recipient_name,
    SUM(federal_action_obligation) AS total_net_spend
FROM spend_transactions
GROUP BY recipient_name
ORDER BY total_net_spend DESC
LIMIT 10;

-- 4. Calculate spending by product/service category

SELECT
    product_or_service_code,
    product_or_service_code_description,
    SUM(federal_action_obligation) AS category_net_spend
FROM spend_transactions
GROUP BY
    product_or_service_code,
    product_or_service_code_description
ORDER BY category_net_spend DESC
LIMIT 10;

-- 5. Calculate the percentage of spending going to the top 10 suppliers

WITH supplier_spending AS (

    SELECT
        recipient_name,
        SUM(federal_action_obligation) AS total_spend

    FROM spend_transactions

    GROUP BY recipient_name

),

ranked_suppliers AS (

    SELECT
        recipient_name,
        total_spend,

        ROW_NUMBER() OVER (
            ORDER BY total_spend DESC
        ) AS supplier_rank

    FROM supplier_spending

)

SELECT
    SUM(total_spend) AS top_10_supplier_spend,

    (SELECT SUM(federal_action_obligation)
     FROM spend_transactions) AS total_net_spend,

    ROUND(
        SUM(total_spend) * 100.0 /
        (SELECT SUM(federal_action_obligation)
         FROM spend_transactions),
        2
    ) AS top_10_spending_percentage

FROM ranked_suppliers
WHERE supplier_rank <= 10;

-- 6. Calculate supplier and award counts

SELECT
    COUNT(DISTINCT recipient_uei) AS total_suppliers,
    COUNT(DISTINCT award_id_piid) AS total_awards,
    COUNT(*) AS total_transactions
FROM spend_transactions;