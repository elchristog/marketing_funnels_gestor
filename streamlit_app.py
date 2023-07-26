UnhashableTypeError: Cannot hash object of type sqlite3.Connection, found in the arguments of get_data().

While caching the arguments of get_data(), Streamlit encountered an object of type sqlite3.Connection, which it does not know how to hash.

To address this, please try helping Streamlit understand how to hash that type by passing the hash_funcs argument into @st.cache. For example:


@st.cache(hash_funcs={sqlite3.Connection: my_hash_func})
def my_func(...):
    ...
If you don't know where the object of type sqlite3.Connection is coming from, try looking at the hash chain below for an object that you do recognize, then pass that to hash_funcs instead:


Object of type sqlite3.Connection: <sqlite3.Connection object at 0x7f407e0fac60>
Object of type builtins.tuple: (<sqlite3.Connection object at 0x7f407e0fac60>, "\n                SELECT\n                    date,\n                    funnel_steps.name,\n                    funnel_steps.order_number,\n                    SUM(registrations.realizations) AS realizations\n                FROM funnel_steps\n                LEFT JOIN registrations ON funnel_steps.id = registrations.funnel_step_id\n                WHERE date(registrations.date) BETWEEN '2023-07-01' AND '2023-07-31'\n                GROUP BY date, funnel_steps.name\n                ORDER BY date, funnel_steps.order_number\n                ")
Please see the hash_funcs documentation for more details.

Traceback:
File "/mount/src/marketing_funnels_gestor/streamlit_app.py", line 158, in <module>
    main()
File "/mount/src/marketing_funnels_gestor/streamlit_app.py", line 143, in main
    df = get_data(conn, f"""
File "/usr/local/lib/python3.9/copyreg.py", line 70, in _reduce_ex
    raise TypeError(f"cannot pickle {cls.__name__!r} object")
