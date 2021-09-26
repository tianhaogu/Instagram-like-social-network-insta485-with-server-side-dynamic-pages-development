"""Views, one for each Insta485 page."""
from insta485.views.index import show_index
from insta485.views.download_file import download_file
from insta485.views.following import show_following, operate_following
from insta485.views.accounts import show_account_create, show_account_delete, show_account_edit, show_account_login, operate_account_logout, operate_accounts
from insta485.views.likecomment import operate_like, operate_comment
from insta485.views.posts import show_post
from insta485.views.user import show_user
from insta485.views.followers import show_followers
from insta485.views.explore import show_explore
