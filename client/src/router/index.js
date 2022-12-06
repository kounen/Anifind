import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
    meta: {
      title: 'Anifind - Home'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
    meta: {
      title: 'Anifind - Register'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: {
      title: 'Anifind - Login'
    }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: {
      title: 'Anifind - Profile'
    }
  },
  {
    path: '/redirect',
    name: 'MALOauth',
    component: () => import('../views/MALoauthRedirect.vue'),
    meta: {
      title: 'Wait..'
    }
  },
  {
    path: '/disconnect',
    name: 'disconnect',
    component: () => import('../views/DisconnectView.vue'),
    meta: {
      title: 'Disconnecting..'
    }
  }
]

const router = createRouter({
  mode: 'history',
  history: createWebHashHistory(),
  routes
})

export default router
