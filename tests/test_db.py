from retail_rag_sim.tools.db import run_select

def test_select_orders():
    rows = run_select("SELECT order_id, status FROM orders LIMIT 1")
    assert len(rows) == 1
