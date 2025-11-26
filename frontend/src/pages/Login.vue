<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 - 现代设计 -->
    <header class="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50 border-b border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
              </svg>
            </div>
            <h1 class="text-2xl md:text-3xl font-bold bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 bg-clip-text text-transparent">
              InspireEd
            </h1>
          </div>
          <button
            v-if="!showLoginForm"
            @click="showLoginForm = true"
            class="px-6 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl hover:from-emerald-600 hover:to-teal-600 font-medium shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transition-all transform hover:scale-105"
          >
            登录
          </button>
          <button
            v-else
            @click="showLoginForm = false"
            class="px-6 py-2.5 border-2 border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-300 font-medium transition-all"
          >
            返回
          </button>
        </div>
      </div>
    </header>

    <!-- Hero 区域 - 现代设计 -->
    <section v-if="!showLoginForm" class="relative overflow-hidden bg-gradient-to-br from-slate-50 via-emerald-50/30 to-teal-50/50 py-24">
      <!-- 装饰性背景元素 -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-emerald-200/40 to-teal-200/40 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-cyan-200/40 to-blue-200/40 rounded-full blur-3xl"></div>
        <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-teal-100/30 to-emerald-100/30 rounded-full blur-3xl"></div>
      </div>
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div class="inline-block mb-6 px-4 py-2 bg-emerald-100/80 backdrop-blur-sm rounded-full border border-emerald-200/50">
          <span class="text-sm font-semibold text-emerald-700">✨ 探究式STEM教学系统</span>
        </div>
        <h2 class="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-emerald-700 to-teal-700 bg-clip-text text-transparent">
          交互式学习活动平台
        </h2>
        <p class="text-xl md:text-2xl mb-4 text-gray-700 font-medium">
          基于建构主义的探究式STEM教学系统
        </p>
        <p class="text-lg md:text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
          系统化课程设计 · 结构化活动单元 · 数据驱动教学 · 持续质量改进
        </p>
        
        <!-- 统计数据 -->
        <div class="flex flex-wrap justify-center gap-8 md:gap-16 mt-16">
          <div class="group text-center bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:scale-105 border border-white/50">
            <div class="text-5xl md:text-6xl font-bold mb-2 bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">100+</div>
            <div class="text-base md:text-lg text-gray-700 font-medium">结构化学习单元</div>
          </div>
          <div class="group text-center bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:scale-105 border border-white/50">
            <div class="text-5xl md:text-6xl font-bold mb-2 bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">200+</div>
            <div class="text-base md:text-lg text-gray-700 font-medium">交互式仿真实验</div>
          </div>
          <div class="group text-center bg-white/60 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all transform hover:scale-105 border border-white/50">
            <div class="text-5xl md:text-6xl font-bold mb-2 bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">500+</div>
            <div class="text-base md:text-lg text-gray-700 font-medium">教学实践案例</div>
          </div>
        </div>
      </div>
    </section>

    <!-- 学科分类 - 现代设计 -->
    <section v-if="!showLoginForm" class="py-20 bg-gradient-to-b from-white to-slate-50/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-3">探索学科</h3>
          <p class="text-gray-600 text-lg">选择您感兴趣的学科领域开始学习</p>
        </div>
        
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 md:gap-6">
          <!-- 人工智能 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'computer' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-orange-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-orange-500 via-orange-500 to-amber-500 p-8 text-white shadow-lg shadow-orange-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-orange-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">🤖</div>
                <h4 class="text-xl font-bold mb-2">人工智能</h4>
                <p class="text-sm text-orange-100">AI</p>
              </div>
            </div>
          </RouterLink>
          <!-- 数学 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'math' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-green-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 via-green-500 to-teal-500 p-8 text-white shadow-lg shadow-emerald-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-emerald-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">📐</div>
                <h4 class="text-xl font-bold mb-2">数学</h4>
                <p class="text-sm text-emerald-100">Math</p>
              </div>
            </div>
          </RouterLink>

          <!-- 物理 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'physics' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-blue-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500 via-blue-500 to-indigo-500 p-8 text-white shadow-lg shadow-cyan-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-cyan-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">⚛️</div>
                <h4 class="text-xl font-bold mb-2">物理</h4>
                <p class="text-sm text-cyan-100">Physics</p>
              </div>
            </div>
          </RouterLink>

          <!-- 化学 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'chemistry' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-purple-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-500 via-purple-500 to-fuchsia-500 p-8 text-white shadow-lg shadow-violet-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-violet-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">🧪</div>
                <h4 class="text-xl font-bold mb-2">化学</h4>
                <p class="text-sm text-violet-100">Chemistry</p>
              </div>
            </div>
          </RouterLink>

          <!-- 生物 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'biology' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-pink-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-rose-500 via-pink-500 to-fuchsia-500 p-8 text-white shadow-lg shadow-rose-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-rose-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">🧬</div>
                <h4 class="text-xl font-bold mb-2">生物</h4>
                <p class="text-sm text-rose-100">Biology</p>
              </div>
            </div>
          </RouterLink>

          <!-- 地球科学 -->
          <RouterLink
            :to="{ name: 'SubjectCourses', params: { subjectCode: 'geography' } }"
            class="group block rounded-2xl focus:outline-none focus-visible:ring-4 focus-visible:ring-yellow-200"
          >
            <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-amber-500 via-yellow-500 to-orange-500 p-8 text-white shadow-lg shadow-amber-500/20 transition-all duration-300 transform group-hover:shadow-2xl group-hover:shadow-amber-500/30 group-hover:scale-105 group-hover:-translate-y-1">
              <div class="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div class="relative text-center">
                <div class="w-16 h-16 mx-auto mb-4 flex items-center justify-center text-5xl leading-none transform group-hover:scale-110 transition-transform">🌍</div>
                <h4 class="text-xl font-bold mb-2">地球科学</h4>
                <p class="text-sm text-amber-100">Earth Science</p>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 特色功能 - 现代设计 -->
    <section v-if="!showLoginForm" class="py-20 bg-gradient-to-b from-slate-50/50 to-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-12">
          <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-3">PDCA教学质量管理循环</h3>
          <p class="text-center text-gray-600 text-lg max-w-3xl mx-auto">基于循证教育理念，实现课程设计-教学实施-评估分析-持续改进的完整闭环</p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <!-- 1. Plan - 系统化课程设计 -->
          <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-violet-500">
            <div class="w-14 h-14 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-violet-500/20 group-hover:shadow-xl group-hover:shadow-violet-500/30 transition-all">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
            </div>
            <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Plan · 系统化设计</h4>
            <p class="text-sm text-gray-600 text-center leading-relaxed">基于布鲁姆分类法和能力本位框架，构建层次化知识图谱与学习目标体系</p>
          </div>

          <!-- 2. Do - 结构化活动实施 -->
          <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-cyan-500">
            <div class="w-14 h-14 bg-gradient-to-br from-cyan-500 to-teal-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-cyan-500/20 group-hover:shadow-xl group-hover:shadow-cyan-500/30 transition-all">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path>
              </svg>
            </div>
            <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Do · 结构化实施</h4>
            <p class="text-sm text-gray-600 text-center leading-relaxed">整合多模态教学资源，支持5E教学模型，创建符合学习科学的活动序列</p>
          </div>

          <!-- 3. Check - 探究式学习过程 -->
          <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-emerald-500">
            <div class="w-14 h-14 bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-emerald-500/20 group-hover:shadow-xl group-hover:shadow-emerald-500/30 transition-all">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
              </svg>
            </div>
            <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Check · 过程性评估</h4>
            <p class="text-sm text-gray-600 text-center leading-relaxed">基于建构主义理论的探究式学习，多维度采集认知过程数据与学习行为轨迹</p>
          </div>

          <!-- 4. Act - 数据驱动改进 -->
          <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-amber-500">
            <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-amber-500/20 group-hover:shadow-xl group-hover:shadow-amber-500/30 transition-all">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
            </div>
            <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Act · 循证改进</h4>
            <p class="text-sm text-gray-600 text-center leading-relaxed">运用学习分析技术，生成可操作的教学洞察，支持循证决策与持续改进</p>
          </div>
        </div>

        <!-- 双循环连接图示 -->
        <div class="mt-16 mb-8 text-center">
          <div class="inline-flex items-center justify-center space-x-4 text-gray-400">
            <div class="h-px w-16 bg-gray-300"></div>
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"></path>
            </svg>
            <div class="h-px w-16 bg-gray-300"></div>
          </div>
          <p class="text-sm text-gray-500 mt-2">双循环协同：教学管理循环驱动学习活动循环</p>
        </div>

        <!-- 5E科学学习循环 -->
        <div class="mt-8">
          <h3 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4 text-center">5E科学学习活动循环</h3>
          <p class="text-center text-gray-600 mb-12 text-lg">基于建构主义的探究式学习模型，引导学生主动构建知识</p>
          
          <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 w-full">
            <!-- 1. Engage - 参与投入 -->
            <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-rose-500">
              <div class="w-14 h-14 bg-gradient-to-br from-rose-500 to-pink-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-rose-500/20 group-hover:shadow-xl group-hover:shadow-rose-500/30 transition-all">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Engage<br/>参与投入</h4>
              <p class="text-sm text-gray-600 text-center leading-relaxed">激发好奇心，引发认知冲突，建立学习动机</p>
            </div>

            <!-- 2. Explore - 探索发现 -->
            <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-cyan-500">
              <div class="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-cyan-500/20 group-hover:shadow-xl group-hover:shadow-cyan-500/30 transition-all">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </div>
              <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Explore<br/>探索发现</h4>
              <p class="text-sm text-gray-600 text-center leading-relaxed">动手实验，收集数据，观察现象，形成初步想法</p>
            </div>

            <!-- 3. Explain - 解释建构 -->
            <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-amber-500">
              <div class="w-14 h-14 bg-gradient-to-br from-amber-500 to-yellow-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-amber-500/20 group-hover:shadow-xl group-hover:shadow-amber-500/30 transition-all">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
                </svg>
              </div>
              <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Explain<br/>解释建构</h4>
              <p class="text-sm text-gray-600 text-center leading-relaxed">表达理解，建构概念，形成科学解释</p>
            </div>

            <!-- 4. Elaborate - 深化拓展 -->
            <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-teal-500">
              <div class="w-14 h-14 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-teal-500/20 group-hover:shadow-xl group-hover:shadow-teal-500/30 transition-all">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                </svg>
              </div>
              <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Elaborate<br/>深化拓展</h4>
              <p class="text-sm text-gray-600 text-center leading-relaxed">应用新知，迁移概念，解决新问题</p>
            </div>

            <!-- 5. Evaluate - 评价反思 -->
            <div class="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1 border-x border-b border-gray-100 border-t-4 !border-t-indigo-500">
              <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg shadow-indigo-500/20 group-hover:shadow-xl group-hover:shadow-indigo-500/30 transition-all">
                <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h4 class="text-lg font-bold text-gray-900 mb-2 text-center">Evaluate<br/>评价反思</h4>
              <p class="text-sm text-gray-600 text-center leading-relaxed">评估理解，反思过程，形成元认知</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 登录表单区域 -->
    <section v-if="showLoginForm" class="py-16">
      <div class="max-w-md mx-auto px-4">
        <div class="bg-white rounded-2xl shadow-xl p-8">
          <div class="mb-8 text-center">
            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              {{ isLogin ? '欢迎回来' : '创建账户' }}
            </h2>
            <p class="text-gray-600">
              {{ isLogin ? '登录到您的账户继续学习' : '注册新账户开始您的学习之旅' }}
            </p>
          </div>
          
          <form class="space-y-5" @submit.prevent="handleSubmit">
            <!-- 邮箱输入（仅注册时显示） -->
            <div v-if="!isLogin">
              <label class="block text-sm font-medium text-gray-700 mb-2">邮箱地址</label>
              <input
                v-model="form.email"
                type="email"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-xl bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200"
                placeholder="your.email@example.com"
              />
            </div>
            
            <!-- 用户名输入 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">用户名</label>
              <input
                v-model="form.username"
                type="text"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-xl bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200"
                placeholder="请输入用户名"
              />
            </div>
            
            <!-- 密码输入 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">密码</label>
              <input
                v-model="form.password"
                type="password"
                required
                class="block w-full px-4 py-3 border border-gray-300 rounded-xl bg-white text-gray-900 placeholder-gray-400 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all duration-200"
                placeholder="请输入密码"
              />
            </div>

            <!-- 错误提示 -->
            <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {{ error }}
            </div>

            <!-- 提交按钮 -->
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-xl text-white font-medium bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:scale-[1.02]"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                处理中...
              </span>
              <span v-else>{{ isLogin ? '登录' : '注册' }}</span>
            </button>

            <!-- 切换登录/注册 -->
            <div class="text-center pt-4">
              <button
                type="button"
                @click="toggleMode"
                class="text-sm text-emerald-600 hover:text-emerald-500 font-medium transition-colors"
              >
                {{ isLogin ? '还没有账户？立即注册' : '已有账户？立即登录' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>

    <!-- 底部信息 - 现代设计 -->
    <footer class="relative bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 text-white py-16 overflow-hidden">
      <!-- 装饰性背景元素 -->
      <div class="absolute inset-0 overflow-hidden opacity-20">
        <div class="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-emerald-500/30 to-teal-500/30 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-br from-cyan-500/30 to-blue-500/30 rounded-full blur-3xl"></div>
      </div>
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10 xl:gap-12 mb-10">
          <!-- 关于 InspireEd -->
          <div class="text-left sm:col-span-2 lg:col-span-1">
            <div class="flex items-center mb-4">
              <div class="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                </svg>
              </div>
              <h4 class="text-xl font-bold ml-3 bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">InspireEd</h4>
            </div>
            <p class="text-gray-300 text-sm leading-relaxed mb-4">
              基于建构主义学习理论与循证教育理念的交互式STEM教学平台。整合探究式学习、计算思维培养与学习分析技术，构建PDCA教学质量管理循环。
            </p>
            <div class="pt-4 border-t border-slate-700/30">
              <p class="text-sm text-gray-400 leading-relaxed">
                © 2025 <span class="text-emerald-400 font-semibold">InspireEd</span>. 探究式STEM教学系统
                <span class="text-gray-500"> · </span>
                <span class="text-gray-500 text-xs">Evidence-based Learning & Teaching Platform</span>
              </p>
            </div>
          </div>
          
          <!-- 相关链接 -->
          <div class="text-left">
            <h4 class="text-lg font-bold mb-4 text-white">相关链接</h4>
            <ul class="space-y-2.5 text-sm">
              <li>
                <a 
                  href="https://basic.smartedu.cn" 
                  target="_blank" 
                  class="inline-flex items-center text-gray-300 hover:text-emerald-400 transition-colors group"
                >
                  <svg class="w-4 h-4 mr-2 group-hover:translate-x-1 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                  </svg>
                  国家中小学智慧教育平台
                </a>
              </li>
              <li>
                <a 
                  href="https://phet.colorado.edu" 
                  target="_blank" 
                  class="inline-flex items-center text-gray-300 hover:text-emerald-400 transition-colors group"
                >
                  <svg class="w-4 h-4 mr-2 group-hover:translate-x-1 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                  </svg>
                  PhET 交互式模拟
                </a>
              </li>
              <li>
                <span class="inline-flex items-center text-gray-400">
                  <svg class="w-4 h-4 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                  更多教育资源
                </span>
              </li>
            </ul>
          </div>
          
          <!-- 联系与语言 -->
          <div class="text-left">
            <h4 class="text-lg font-bold mb-4 text-white">联系与设置</h4>
            <div class="space-y-4">
              <div>
                <label class="block text-sm text-gray-400 mb-2 font-medium">语言选择</label>
                <select class="bg-slate-800/50 backdrop-blur-sm text-white px-4 py-2.5 rounded-xl text-sm border border-slate-700 hover:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all cursor-pointer w-full">
                  <option>简体中文</option>
                  <option>English</option>
                </select>
              </div>
              <div>
                <p class="text-sm text-gray-400 mb-2">
                  作者：<span class="text-gray-300">广东省开平市教师发展中心 廖作东</span>
                </p>
                <p class="text-sm text-gray-400">
                  <a 
                    href="mailto:382241106@qq.com" 
                    class="inline-flex items-center text-gray-300 hover:text-emerald-400 transition-colors group"
                  >
                    <svg class="w-4 h-4 mr-2 group-hover:scale-110 transition-transform flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                    </svg>
                    382241106@qq.com
                  </a>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { authService } from '../services/auth'
import { UserRole } from '../types/user'

const router = useRouter()
const userStore = useUserStore()

const showLoginForm = ref(false)
const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const form = ref({
  email: '',
  username: '',
  password: '',
})

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
}

async function handleSubmit() {
  loading.value = true
  error.value = ''

  try {
    if (isLogin.value) {
      // 登录
      const tokenResponse = await authService.login({
        username: form.value.username,
        password: form.value.password,
      })
      
      userStore.setToken(tokenResponse.access_token)
      
      const user = await authService.getCurrentUser()
      userStore.setUser(user)
      
      // 根据角色跳转
      let targetPath = ''
      if (user.role === UserRole.ADMIN) {
        targetPath = '/admin'
      } else if (user.role === UserRole.TEACHER) {
        targetPath = '/teacher'
      } else if (user.role === UserRole.STUDENT) {
        targetPath = '/student'
      } else if (user.role === UserRole.RESEARCHER) {
        targetPath = '/researcher'
      } else {
        error.value = '用户角色配置错误，请联系管理员'
        return
      }
      
      await router.push(targetPath)
    } else {
      // 注册
      await authService.register({
        email: form.value.email,
        username: form.value.username,
        password: form.value.password,
        role: UserRole.STUDENT,
      })
      
      error.value = '注册成功！请登录'
      isLogin.value = true
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>
