
```
.
├── App.vue
├── api
│   ├── core
│   │   ├── ApiError.ts
│   │   ├── ApiRequestOptions.ts
│   │   ├── ApiResult.ts
│   │   ├── CancelablePromise.ts
│   │   ├── OpenAPI.ts
│   │   └── request.ts
│   ├── index.ts
│   ├── schemas.gen.ts
│   ├── sdk.gen.ts
│   └── types.gen.ts
├── assets
│   ├── css
│   │   ├── base.css
│   │   ├── box-sizing.css
│   │   └── main.css
│   ├── images
│   │   └── logo.svg
│   └── icons
├── components
│   ├── common
│   │   ├── Navbar.vue
│   │   ├── Sidebar.vue
│   │   ├── SidebarItems.vue
│   │   ├── UserMenu.vue
│   │   └── NotFound.vue
│   ├── items
│   │   ├── ItemForm.vue
│   │   ├── ItemList.vue
│   │   ├── ItemDetails.vue
│   │   └── ItemActions.vue
│   ├── admin
│   │   ├── UserForm.vue
│   │   ├── UserList.vue
│   │   └── UserActions.vue
│   ├── user-settings
│   │   ├── ProfileForm.vue
│   │   ├── PasswordForm.vue
│   │   └── DeleteAccountForm.vue
│   └── ui
│       ├── Button.vue
│       ├── Dialog.vue
│       ├── Input.vue
│       ├── Checkbox.vue
│       ├── Toast.vue
│       └── Pagination.vue
├── composables
│   ├── useAuth.ts
│   ├── useItems.ts
│   ├── useUsers.ts
│   ├── useToast.ts
│   └── usePagination.ts
├── layouts
│   ├── DefaultLayout.vue
│   ├── AdminLayout.vue
│   └── AuthLayout.vue
├── main.ts
├── router
│   └── index.ts
├── stores
│   ├── auth.ts
│   ├── items.ts
│   ├── users.ts
│   └── index.ts
├── types
│   ├── auth.types.ts
│   ├── item.types.ts
│   ├── user.types.ts
│   └── common.types.ts
├── utils
│   ├── error-handler.ts
│   ├── formatters.ts
│   └── validators.ts
└── views
    ├── HomeView.vue
    ├── auth
    │   ├── LoginView.vue
    │   ├── SignupView.vue
    │   ├── RecoverPasswordView.vue
    │   └── ResetPasswordView.vue
    ├── items
    │   ├── ItemsView.vue
    │   ├── ItemDetailView.vue
    │   ├── AddItemView.vue
    │   └── EditItemView.vue
    ├── admin
    │   ├── UsersView.vue
    │   ├── AddUserView.vue
    │   └── EditUserView.vue
    └── settings
        ├── SettingsView.vue
        ├── ProfileView.vue
        └── SecurityView.vue
```
