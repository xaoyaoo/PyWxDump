import {createRouter, createWebHashHistory} from 'vue-router'

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'index',
            component: () => import((`@/views/IndexView.vue`))
        },
        {
            path: '/db_init',
            name: 'db_init',
            component: () => import((`@/views/DbInitView.vue`))
        },
        {
            path: '/home',
            name: 'home',
            component: () => import((`@/views/HomeView.vue`))
        },
        {
            path: '/chat',
            name: 'chat',
            component: () => import((`@/views/ChatView.vue`))
        },
        {
            path: '/chat2ui_select',
            name: 'chat2ui_select',
            component: () => import((`@/views/Chat2UiSelectVue.vue`))
        },

        {
            path: '/chat2ui',
            name: 'chat2ui',
            component: () => import((`@/views/Chat2UiView.vue`))
        },
        {
            path: '/contacts',
            name: 'contacts',
            component: () => import((`@/views/ContactsView.vue`))
        },
        {
            path: '/moments',
            name: 'moments',
            component: () => import((`@/views/MomentsView.vue`))
        },
        {
            path: '/favorite',
            name: 'favorite',
            component: () => import((`@/views/FavoriteView.vue`))
        },
        {
            path: '/cleanup',
            name: 'cleanup',
            component: () => import((`@/views/CleanupView.vue`))
        },
        {
            path: '/statistics',
            name: 'statistics',
            component: () => import((`@/views/StatisticsView.vue`))
        },

        // 专业工具
        {
            path: '/wxinfo',
            name: 'wxinfo',
            component: () => import((`@/views/tools/WxinfoView.vue`))
        },
        {
            path: '/bias',
            name: 'bias',
            component: () => import((`@/views/tools/BiasView.vue`))
        },
        {
            path: '/merge',
            name: 'merge',
            component: () => import((`@/views/tools/MergeView.vue`))
        },
        {
            path: '/decrypt',
            name: 'decrypt',
            component: () => import((`@/views/tools/DecryptView.vue`))
        },

        // 其他 关于、帮助、设置
        {
            path: '/about',
            name: 'about',
            // route level code-splitting
            // this generates a separate chunk (About.[hash].js) for this route
            // which is lazy-loaded when the route is visited.
            component: () => import((`@/views/other/AboutView.vue`))
        },
        {
            path: '/help',
            name: 'help',
            component: () => import((`@/views/other/HelpView.vue`))
        },
        {
            path: '/setting',
            name: 'setting',
            component: () => import((`@/views/other/SettingView.vue`))
        },
    ]
})


export default router
