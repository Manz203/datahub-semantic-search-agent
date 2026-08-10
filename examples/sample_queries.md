# Sample Search Outputs

Real outputs from `search_agent.py` running against a local DataHub instance
loaded with the `showcase-ecommerce` sample data pack (67 entities embedded).

These examples show the agent matching on **meaning**, not just keyword
overlap — e.g. a query about "inventory levels" correctly ranks a dataset
whose name doesn't contain the word "inventory" but whose description does,
above datasets that only share the literal word "warehouse".

---

## Query: `warehouse inventory levels`

```
1. [0.720] (dbt) inventories
   Tracks product inventory levels across warehouses...
   urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.inventories,PROD)

2. [0.567] (postgres) warehouses
   urn:li:dataset:(urn:li:dataPlatform:postgres,b2fd91.order_entry_db.order_entry.warehouses,PROD)

3. [0.517] (s3) warehouses
   urn:li:dataset:(urn:li:dataPlatform:s3,b2fd91.demo-data-bucket/order_entry/warehouses,PROD)

4. [0.505] (snowflake) WAREHOUSES
   urn:li:dataset:(urn:li:dataPlatform:snowflake,b2fd91.order_entry_db.order_entry.warehouses,PROD)

5. [0.462] (dbt) warehouses
   Contains information about physical distribution centers...
   urn:li:dataset:(urn:li:dataPlatform:dbt,b2fd91.order_entry_db.order_entry.warehouses,PROD)
```

**Why this matters:** the top result (`inventories`, score 0.720) is the
semantically correct match — the dataset explicitly about inventory
*levels* — even though the query also contains the word "warehouse", which
literally appears in the names of four other datasets. A pure keyword
search would likely rank those four "warehouses" datasets first; this
agent correctly prioritizes the dataset that actually answers the question.

---

## Query: `customer shipping information`

Top results included datasets covering customer shipping and billing
addresses (`addresses`) and the denormalized `order_details` view, which
contains shipping address fields (`shipping_address_line1`,
`shipping_town_city`, `shipping_country`, etc.) — surfaced correctly even
though the query text doesn't exactly match either dataset's name.

---

## Query: `product returns and refunds`

Top results surfaced the `order_details` view (which includes
`return_date`, `return_status`, and related columns) and the `products`
dataset — again matched on semantic relevance to "returns," a concept
described in the data model rather than named directly as a table.
