# Learnings
## core > serializers.py > UserSerializer
> Here we have changed the serializer view so that password is only accepted to access via creating an user, the userDetails will not access the password field.
## Difference between the serializers.Serializer vs serializers.ModelSerializer 
> The main difference is: using ModelSerializer will convert the Model structure to the serializer class while using Serializer we have to define everything from scratch.