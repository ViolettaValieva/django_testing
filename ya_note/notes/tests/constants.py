from django.urls import reverse


NOTE_TITLE = 'Заголовок'
NOTE_TEXT = 'Текст'
NEW_NOTE_TITLE = 'Новый заголовок'
NEW_NOTE_TEXT = 'Новый текст'
SLUG = 'slug'
NEW_SLUG = 'new-slug'

HOME_URL = reverse('notes:home')
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
