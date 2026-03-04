# --- स्कैनिंग लॉजिक के अंदर ---
if accuracy >= min_acc and avg_return >= min_ret:
    res_row = {
        "Stock": ticker.replace(".NS",""), 
        "Accuracy": f"{int(accuracy)}%", 
        "Avg Return": f"{round(avg_return, 2)}%" # यहाँ round का उपयोग करें
    }
    # सभी सालों के डेटा को 2 डिजिट पर राउंड करना
    rounded_yearly_data = {yr: round(val, 2) for yr, val in yearly_data.items()}
    res_row.update(rounded_yearly_data)
    results.append(res_row)

# --- डिस्प्ले (Table) के लिए ---
if results:
    final_df = pd.DataFrame(results)
    
    # यह लाइन सुनिश्चित करेगी कि पूरी टेबल में . के बाद केवल 2 अंक दिखें
    st.dataframe(final_df.style.applymap(color_rets, subset=final_df.columns[3:]).format(precision=2))
