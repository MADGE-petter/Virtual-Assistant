"""Search Handler - Xử lý tìm kiếm."""

import webbrowser
from service.intern import extract_search_query
from controller.handlers.base_handler import BaseHandler


class SearchHandler(BaseHandler):
    """Handler for search queries."""
    
    def handle(self, text):
        """Xử lý tìm kiếm."""
        search_query = extract_search_query(text)
        
        if search_query:
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
            return f"Tôi đã tìm kiếm {search_query} trên Google."
        else:
            return "need_search_query"
