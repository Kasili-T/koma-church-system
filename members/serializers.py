from rest_framework import serializers
from accounts.models import Member, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class MemberSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = Member
        fields = [
            'id',
            'first_name',
            'last_name',
            'other_names',
            'dob',
            'phone',
            'email',
            'address',
            'joined_on',
            'roles',
            'photo',
        ]
