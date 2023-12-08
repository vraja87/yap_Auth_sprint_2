from src.models.entity import LoginHistory, Role, User, UserRoles

users = [  # login, unhashed passwd, User_obj
    ("UserAdmin", "Some_Pass1", User(login="UserAdmin", password="Some_Pass1", first_name="John", last_name="Doe")),
    ("user2", "pass2", User(login="user2", password="pass2", first_name="Jane", last_name="Doe")),
    ("user3", "pass3", User(login="user3", password="pass3", first_name="Stiv", last_name="Some")),
    ("user4", "pass4", User(login="user4", password="pass4", first_name="Steeev", last_name="Smit")),
    ("user5", "pass5", User(login="user5", password="pass5", first_name="Jane", last_name="Summers")),
]

users_obj = [user_ for _, _, user_ in users]


roles = [
    Role(name="administrator", description="Admin role with all permissions"),
    Role(name="unauthorized_user", description="Unauthorized user role"),
    Role(name="authorized_user", description="Regular user role"),
    Role(name="common_subscribe", description="just subscribe"),
    Role(name="fluggegecheimen_subscribe", description="Strange content subscribe"),
]


def get_user_roles(users_: list[User], roles_: list[Role]):
    user_roles = [
        UserRoles(user_id=users_[0].id, role_id=roles_[0].id),
        UserRoles(user_id=users_[1].id, role_id=roles_[1].id),
        UserRoles(user_id=users_[2].id, role_id=roles_[2].id),
        UserRoles(user_id=users_[3].id, role_id=roles_[3].id),
        UserRoles(user_id=users_[4].id, role_id=roles_[4].id),
    ]
    return user_roles


login_histories = [
    LoginHistory(user_id=users_obj[0].id, user_agent="agent1", ip_address="192.168.1.1"),
    LoginHistory(user_id=users_obj[1].id, user_agent="agent2", ip_address="192.168.1.2"),
    LoginHistory(user_id=users_obj[1].id, user_agent="agent3", ip_address="192.168.1.3"),
    LoginHistory(user_id=users_obj[1].id, user_agent="agent4", ip_address="192.168.1.4"),
]