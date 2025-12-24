import streamlit as st


def render_search_interface(
    search_function,
    placeholder_text="Start typing to search...",
    label="Search:",
    help_text="Type at least 2 characters to search",
    min_chars=2,
    session_key="search_selection",
    num_columns=2,
    show_count=True
):
    """
    Reusable search interface component.
    
    Args:
        search_function: Function that takes search_term and returns list of results
        placeholder_text: Placeholder for the search input
        label: Label for the search input
        help_text: Help text for the search input
        min_chars: Minimum characters before triggering search
        session_key: Session state key to store the selected item
        num_columns: Number of columns to display results in
        show_count: Whether to show the count of matching results
    
    Returns:
        tuple: (selected_item, search_query) - selected_item is None if nothing selected
    """
    
    # Search input
    search_query = st.text_input(
        label,
        placeholder=placeholder_text,
        help=help_text,
        key=f"{session_key}_input"
    )
    
    selected_item = None
    
    # Check if user has previously selected an item
    if f'{session_key}_selected' in st.session_state:
        selected_item = st.session_state[f'{session_key}_selected']
        st.success(f"✅ Selected: **{selected_item}**")
        
        # Option to change selection
        if st.button("🔄 Change selection", key=f"{session_key}_change"):
            del st.session_state[f'{session_key}_selected']
            st.rerun()
        
        return selected_item, search_query
    
    # Show search results if user has typed something
    if search_query and len(search_query) >= min_chars:
        # Call the search function
        matching_items = search_function(search_query)
        
        if matching_items:
            if show_count:
                st.markdown(f"**Found {len(matching_items)} matching result(s):**")
            
            # Display matching items as clickable buttons
            cols = st.columns(num_columns)
            for idx, item in enumerate(matching_items):
                # Handle both string items and dict items
                if isinstance(item, dict):
                    display_text = item.get('display_name', item.get('name', str(item)))
                    item_value = item.get('value', display_text)
                else:
                    display_text = str(item)
                    item_value = item
                
                with cols[idx % num_columns]:
                    if st.button(
                        display_text,
                        key=f"{session_key}_item_{idx}",
                        use_container_width=True
                    ):
                        # Store selection in session state
                        st.session_state[f'{session_key}_selected'] = item_value
                        st.rerun()
        else:
            st.warning(f"No results found for '{search_query}'")
    elif search_query and len(search_query) < min_chars:
        st.info(f"💡 Type at least {min_chars} characters to search")
    else:
        st.info(f"💡 {help_text}")
    
    return selected_item, search_query


def clear_search_selection(session_key):
    """Clear the search selection from session state."""
    if f'{session_key}_selected' in st.session_state:
        del st.session_state[f'{session_key}_selected']
