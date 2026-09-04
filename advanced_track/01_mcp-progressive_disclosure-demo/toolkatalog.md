# Toolkatalog

Die folgende Liste dokumentiert den aktuellen Stand. Maßgeblich ist die zur Laufzeit per MCP
ermittelte Toolzahl; Frontend und API verwenden keine fest eingetragene Anzahl.

#	Modul	Tool	Parameter
1	weather	get_weather	city
2	weather	get_forecast	city, days
3	weather	get_humidity	city
4	weather	get_temperature	city
5	weather	get_wind_speed	city
6	weather	get_precipitation	city
7	weather	get_uv_index	city
8	weather	get_air_quality	city
9	weather	get_weather_alerts	city
10	weather	get_sunrise_sunset	city
11	customers	search_customers	query
12	customers	get_customer	customer_id
13	customers	create_customer	name, email, company
14	customers	update_customer	customer_id, name, email
15	customers	delete_customer	customer_id
16	customers	get_customer_orders	customer_id
17	customers	get_customer_invoices	customer_id
18	customers	create_support_ticket	customer_id, title, description, priority
19	customers	get_customer_history	customer_id
20	customers	get_customer_statistics	customer_id
21	customers	merge_customers	primary_id, secondary_id
22	customers	get_customer_communications	customer_id
23	orders	create_order	customer_id, items
24	orders	get_order	order_id
25	orders	list_orders	status, limit
26	orders	cancel_order	order_id, reason
27	orders	update_order	order_id, items, status
28	orders	get_order_status	order_id
29	orders	get_order_tracking	order_id
30	orders	add_order_item	order_id, product_id, quantity, price
31	orders	remove_order_item	order_id, product_id
32	orders	get_order_invoice	order_id
33	orders	ship_order	order_id, carrier, address
34	orders	get_order_history	order_id
35	finance	get_invoice	invoice_id
36	finance	create_invoice	customer_id, items
37	finance	calculate_tax	amount, region
38	finance	process_payment	invoice_id, amount, method
39	finance	get_payment_status	payment_id
40	finance	get_financial_report	start_date, end_date
41	finance	get_balance_sheet	date
42	finance	get_income_statement	start_date, end_date
43	finance	get_cash_flow	start_date, end_date
44	finance	create_budget	name, amount, period
45	finance	get_budget_status	budget_id
46	finance	get_expenses	start_date, end_date, category
47–101	dummy	analyze_data ... validate_data	value (jeweils 1 Parameter)

Aktueller Stand: 10 Wetter- + 12 Kunden- + 12 Bestell- + 12 Finanz- + 55 Betriebs-Tools = 101.
