from django.db.models import Q
from simple_search import BaseSearchForm

from users.models import User, School

class UserSearchForm(BaseSearchForm):
    class Meta:
        base_qs = User.objects
        search_fields = ('^name', 'description', 'specifications', '=id') 

        # assumes a fulltext index has been defined on the fields
        # 'name,description,specifications,id'
        fulltext_indexes = (
            ('name', 2), # name matches are weighted higher
            ('name,description,specifications,id', 1),
        )
