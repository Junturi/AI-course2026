# Overview 

The demo8.1 is a fixed script — all quantities, vendors, and prices are hardcoded. And most importantly, there is no real decision to be made.  

Your job is to build it into a real, dynamic agent across four tasks. 

## Task 1 — Dynamic Quantity via Tool Call 

**Goal:** Replace the hardcoded `fetch_pricing` node with a tool-based approach. 

The `fetch_pricing` node currently hardcodes 50 units at fixed prices. Replace it so that: 

The request string (e.g. "Order 30 laptops for the sales team") is parsed to extract the quantity. 

A `get_unit_price(vendor: str) -> float` tool is defined and bound to the LLM. 

The LLM calls the tool once per vendor to get the unit price. 

The node calculates `total = unit_price * quantity` and stores that in quotes. 

You may keep the unit prices hardcoded inside the tool for now (Task 4 will fix that). 





## Task 2 — Conditional Interrupt 

**Goal:** The interrupt in `request_approval` currently always fires. Make it conditional. 

Change the graph so that: 

After compare_quotes, a routing function checks whether `best_quote["total"]` exceeds €10,000. 

If yes — route to `request_approval` (interrupt, wait for manager). 

If no — skip `request_approval` entirely and go straight to `submit_purchase_order`. 

> Hint: Use add_conditional_edges on the compare_quotes node. 



## Task 3 — Handle Rejection Gracefully 

**Goal:** When the manager rejects the purchase, the graph currently sets po_number = "REJECTED" and limps to the end. Make rejection a proper outcome. 

Change the graph so that: 

After `request_approval`, a routing function reads `approval_status`. 

If approved — continue to submit_purchase_order. 

If rejected — skip submit_purchase_order and go directly to notify_employee, passing a clear rejection reason in state using the approval_status or add a new state field optionally for more details.  

The `notify_employee` node must handle both cases cleanly (it already has an if/else — keep it, but make sure it gets the right context). 

To test: run with `--resume` and pass `"Rejected — over budget"` as the resume value instead of the approval string. 





## Task 4 — Real Data from dummyjson.com 

**Goal:** Replace the hardcoded unit prices in your tool with live data from a real API. 

Update and/or replace the `get_unit_price tool` and `lookup_vendors`, `fetch_pricing` node functions to: 

Fetch `https://dummyjson.com/products/category/laptops` 

Search the returned products for those with cheapest price and availability within 2 weeks.  

Use that product price as the unit price and calculcate the total price. Pass the product information forward in the chain so that correct product name is used in the approval request.  

If no match is found, fall back to a sensible default and log a warning. 