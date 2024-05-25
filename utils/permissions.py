from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist

from apps.team.models import Team



class BasePermission(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True
        # By default, don't allow access
        return False

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        # If the user is a super admin, allow access
        if super().has_permission(request, view):
            return True
        # Otherwise, check if the user is a student
        if request.user and request.user.groups.filter(name='Student'):
            return True
        return False
class IsLeaderOrMembers(BasePermission):
    def has_permission(self, request, view):
        
        if super().has_permission(request, view):
            return True
        
        team_id = view.kwargs.get('team_id')
        if not team_id:
            return False
        try:
            team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return False
        return team.leader == request.user or request.user in team.members.all()
    

class IsLecturer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Lecturer'):
            return True
        return False
    
class IsLecturerReviewer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='LecturerReviewer'):
            return True
        return False

    
class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Supervisor'):
            return True
        return False

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Admin'):
            return True
        return False
    
class isSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        
class IsLeaderOrMembersTeamOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        team_id = view.kwargs.get('team_id')
        if not team_id:
            return False
        try:
            team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return False
        return team.leader == request.user or request.user in team.members.all()
    
    
class IsGuest(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Guest'):
            return True
        return False

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS request.
        if request.method in permissions.SAFE_METHODS:
            return True
    
        return obj == request.user
    
class IsTeamLeader(permissions.BasePermission):
    """
    Custom permission to only allow team leaders to invite members.
    """
    
    def has_permission(self, request, view):
        team_id = request.data.get('team_id')
        if not team_id:
            return False

        try:
            team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return False
        return team.leader == request.user
    
class IsMember(permissions.BasePermission):
    """
    Custom permission to only allow team members to view the team.
    """
    
    def has_permission(self, request, view):
        team_id = request.data.get('team_id')
        if not team_id:
            return False
        try:
            team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return False
        return request.user in team.members.all()
    
class IsTeamLeaderOrMember(permissions.BasePermission):
    """
    Custom permission to only allow team leaders or team members to access the team.
    """

    def has_permission(self, request, view):
        team_id = view.kwargs.get('team_id')
        if not team_id:
            return False
    
        try:
            team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return False
        if team.leader is None:
            return False
    
        return team.leader.user == request.user or request.user in team.members.all()
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin to edit it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff