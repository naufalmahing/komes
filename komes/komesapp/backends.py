from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import PermissionDenied

class CustomBackend(ModelBackend):
    def get_all_permissions(self, user_obj, obj=None):
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()
        if not hasattr(user_obj, "_perm_cache"):
            user_obj._perm_cache = super().get_all_permissions(user_obj)
        return user_obj._perm_cache
    
    def has_perm(self, user_obj, perm, obj=None):
        # return super().has_perm(user_obj, perm, obj)
        # raise PermissionDenied
        print('this', obj)
        print(perm)
        print(user_obj)

        print(super().has_perm(user_obj, perm, obj))
        if super().has_perm(user_obj, perm, obj):
            if obj:
                if obj.store.name == user_obj.store.name:
                    print('user  have permission')
                    return True
                
                # print('user dont have permission')
                print('this is not allowed')

                # return True
                raise PermissionDenied
            return True
        
        return False
    
    # def has_perm(self, user_obj, perm, obj=None):
    #     if user_obj.store:
    #         if user_obj.store.id == obj.id:
    #             return True
    #     return False
    #     try:
    #         print('this')

    #     except Exception as _:
    #         raise PermissionDenied
    #     return super().has_perm(user_obj, perm, obj)