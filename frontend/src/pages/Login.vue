<template>
  <div class="min-h-screen bg-slate-50 font-sans selection:bg-emerald-100 selection:text-emerald-900">
    <!-- 顶部导航栏 - 玻璃拟态设计 -->
    <header
      class="fixed w-full top-0 z-50 transition-all duration-300"
      :class="isScrolled ? 'bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200/50 py-2' : 'bg-transparent py-4'"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between">
          <!-- Logo -->
          <div class="flex items-center space-x-3 group cursor-pointer" @click="showLoginForm = false">
            <div
              class="w-10 h-10 bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 group-hover:scale-105 transition-transform duration-300 ring-2 ring-white/50"
            >
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2.5"
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                ></path>
              </svg>
            </div>
            <span
              class="text-2xl font-bold bg-gradient-to-r from-slate-800 via-slate-700 to-slate-900 bg-clip-text text-transparent tracking-tight group-hover:opacity-80 transition-opacity"
            >
              InspireEd
            </span>
          </div>

          <!-- Action Button -->
          <button
            @click="showLoginForm = !showLoginForm"
            class="relative inline-flex group"
          >
            <div
              class="absolute transition-all duration-1000 opacity-70 -inset-px bg-gradient-to-r from-[#44BC87] via-[#42b883] to-[#FF44EC] rounded-full blur-lg group-hover:opacity-100 group-hover:-inset-1 group-hover:duration-200 animate-tilt"
            ></div>
            <div
              class="relative px-6 py-2.5 bg-white rounded-full leading-none flex items-center space-x-2 border border-slate-100 shadow-sm transition duration-200 group-hover:bg-slate-50"
            >
              <span class="font-semibold text-slate-700 group-hover:text-emerald-600 transition-colors">
                {{ showLoginForm ? '返回首页' : '登录 / 注册' }}
              </span>
              <svg 
                v-if="!showLoginForm"
                class="w-4 h-4 text-slate-400 group-hover:text-emerald-500 group-hover:translate-x-0.5 transition-all" 
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
              <svg 
                v-else
                class="w-4 h-4 text-slate-400 group-hover:text-emerald-500 group-hover:-translate-x-0.5 transition-all" 
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </div>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="relative pt-24 min-h-screen flex flex-col">
      
      <!-- Scene 1: Landing Page Content -->
      <transition
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="opacity-0 translate-y-4"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition duration-300 ease-in absolute w-full"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-4"
      >
        <div v-if="!showLoginForm" class="flex-grow">
          <!-- Hero Section -->
          <section class="relative overflow-hidden pb-16 lg:pb-24">
            <!-- Dynamic Background Gradients -->
            <div class="absolute inset-0 pointer-events-none">
              <div 
                class="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-b from-emerald-50/80 via-teal-50/50 to-transparent rounded-[100%] blur-3xl -z-10 transition-colors duration-1000"
                :class="currentSystem === 'evaluation' ? '!from-teal-50/80 !via-emerald-50/50' : ''"
              ></div>
              <div class="absolute top-20 right-0 w-96 h-96 bg-cyan-100/40 rounded-full blur-3xl -z-10 mix-blend-multiply animate-blob"></div>
              <div class="absolute top-40 left-0 w-96 h-96 bg-emerald-100/40 rounded-full blur-3xl -z-10 mix-blend-multiply animate-blob animation-delay-2000"></div>
            </div>

            <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
              <!-- System Switcher Pills -->
              <div class="flex justify-center mb-10">
                <div class="bg-slate-100/80 backdrop-blur-sm p-1.5 rounded-full border border-slate-200/60 inline-flex shadow-inner">
                  <button
                    v-for="sys in [
                      { id: 'learning', icon: '📚', label: '交互式学习平台', color: 'text-emerald-700' },
                      { id: 'evaluation', icon: '📊', label: '教学增值评价', color: 'text-teal-700' }
                    ]"
                    :key="sys.id"
                    @click="currentSystem = sys.id as any"
                    class="px-6 py-2.5 rounded-full text-sm font-bold transition-all duration-300 flex items-center space-x-2 relative overflow-hidden"
                    :class="currentSystem === sys.id ? 'bg-white shadow-md text-slate-800 scale-105 ring-1 ring-black/5' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'"
                  >
                    <span class="text-lg">{{ sys.icon }}</span>
                    <span :class="currentSystem === sys.id ? sys.color : ''">{{ sys.label }}</span>
                  </button>
                </div>
              </div>

              <!-- Hero Text Content -->
              <div class="relative min-h-[300px]">
                <!-- Learning Content -->
                <div
                  class="transition-all duration-700 absolute inset-0 flex flex-col items-center"
                  :class="currentSystem === 'learning' ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-8 scale-95 pointer-events-none'"
                >
                  <div class="inline-flex items-center space-x-2 mb-6 px-4 py-1.5 bg-emerald-50 rounded-full border border-emerald-100 shadow-sm">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    <span class="text-xs font-bold text-emerald-800 tracking-wide uppercase">探究式 STEM 教学系统</span>
                  </div>
                  
                  <h1 class="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight text-slate-900 leading-[1.1]">
                    交互式<span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500">学习活动</span>平台
                  </h1>
                  
                  <p class="text-xl md:text-2xl text-slate-600 mb-8 max-w-3xl mx-auto leading-relaxed font-light">
                    基于<span class="font-medium text-slate-800">建构主义</span>的探究式学习，让每一次实验都充满发现的乐趣。
                  </p>

                  <div class="flex flex-wrap justify-center gap-6 mt-4">
                    <div v-for="(stat, idx) in [
                      { num: '100+', label: '结构化单元', from: 'from-emerald-500', to: 'to-teal-500' },
                      { num: htmlResourceCount ? `${htmlResourceCount}+` : '...', label: '仿真实验', from: 'from-teal-500', to: 'to-cyan-500' },
                      { num: lessonCount ? `${lessonCount}+` : '...', label: '实践案例', from: 'from-cyan-500', to: 'to-blue-500' }
                    ]" :key="idx" 
                    class="bg-white/60 backdrop-blur-md border border-white/60 px-8 py-4 rounded-2xl shadow-lg shadow-slate-200/50 hover:-translate-y-1 transition-transform duration-300">
                      <div class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r" :class="[stat.from, stat.to]">
                        {{ stat.num }}
                      </div>
                      <div class="text-xs text-slate-500 font-semibold uppercase tracking-wider mt-1">{{ stat.label }}</div>
                    </div>
                  </div>
                </div>

                <!-- Evaluation Content -->
                <div
                  class="transition-all duration-700 absolute inset-0 flex flex-col items-center"
                  :class="currentSystem === 'evaluation' ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-8 scale-95 pointer-events-none'"
                >
                  <div class="inline-flex items-center space-x-2 mb-6 px-4 py-1.5 bg-teal-50 rounded-full border border-teal-100 shadow-sm">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
                    </span>
                    <span class="text-xs font-bold text-teal-800 tracking-wide uppercase">核心功能升级</span>
                  </div>

                  <h1 class="text-5xl md:text-7xl font-extrabold mb-6 tracking-tight text-slate-900 leading-[1.1]">
                    教学<span class="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-emerald-500">增值评价</span>系统
                  </h1>
                  
                  <p class="text-xl md:text-2xl text-slate-600 mb-8 max-w-3xl mx-auto leading-relaxed font-light">
                    超越绝对成绩，关注<span class="font-medium text-slate-800">“进步幅度”</span>与<span class="font-medium text-slate-800">“净增值”</span>。
                  </p>

                  <div class="flex flex-wrap justify-center gap-4 mt-4">
                    <span v-for="(feat, idx) in ['首尾对比模型', '率指标增值', '精准诊断', '科学排除生源影响']" :key="idx"
                      class="px-5 py-2 bg-teal-50/50 border border-teal-100 text-teal-700 rounded-full font-medium text-sm hover:bg-teal-100 transition-colors cursor-default">
                      {{ feat }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </section>

            <!-- Learning Modules Grid -->
            <section v-if="currentSystem === 'learning'" class="py-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <RouterLink
                  v-for="subject in [
                    { code: 'computer', name: '人工智能', en: 'AI', icon: '🤖', color: 'from-orange-400 to-amber-500', shadow: 'shadow-orange-500/20' },
                    { code: 'math', name: '数学', en: 'Math', icon: '📐', color: 'from-emerald-400 to-green-500', shadow: 'shadow-emerald-500/20' },
                    { code: 'physics', name: '物理', en: 'Physics', icon: '⚛️', color: 'from-cyan-400 to-blue-500', shadow: 'shadow-cyan-500/20' },
                    { code: 'chemistry', name: '化学', en: 'Chemistry', icon: '🧪', color: 'from-violet-400 to-purple-500', shadow: 'shadow-violet-500/20' },
                    { code: 'biology', name: '生物', en: 'Biology', icon: '🧬', color: 'from-rose-400 to-pink-500', shadow: 'shadow-rose-500/20' },
                    { code: 'geography', name: '地球科学', en: 'Earth Science', icon: '🌍', color: 'from-amber-400 to-yellow-500', shadow: 'shadow-amber-500/20' }
                  ]"
                  :key="subject.code"
                  :to="{ name: 'SubjectCourses', params: { subjectCode: subject.code } }"
                  class="group relative overflow-hidden rounded-2xl bg-white p-6 shadow-sm border border-slate-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
                >
                  <div class="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br opacity-10 rounded-full blur-2xl -mr-8 -mt-8 transition-opacity group-hover:opacity-20" :class="subject.color"></div>
                  <div class="relative z-10 flex flex-col items-center">
                    <div class="text-4xl mb-3 transform group-hover:scale-110 transition-transform duration-300 filter drop-shadow-sm">{{ subject.icon }}</div>
                    <h3 class="font-bold text-slate-800 text-lg group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r" :class="subject.color">{{ subject.name }}</h3>
                    <p class="text-xs text-slate-400 font-medium tracking-wide uppercase mt-1">{{ subject.en }}</p>
                  </div>
                </RouterLink>
              </div>
            </section>

            <!-- Features Section -->
            <section class="py-16 bg-white/50 border-t border-slate-100">
              <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <!-- Learning System: PDCA & 5E -->
                <div v-if="currentSystem === 'learning'" class="animate-fade-in">
                  <div class="text-center mb-12">
                    <h2 class="text-3xl font-bold text-slate-900">PDCA 教学质量管理循环</h2>
                    <p class="mt-4 text-lg text-slate-600">构建完整的闭环教学管理体系</p>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <div v-for="(item, idx) in [
                      { title: 'Plan · 系统化设计', desc: '基于布鲁姆分类法和能力本位框架', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2', color: 'bg-violet-500' },
                      { title: 'Do · 结构化实施', desc: '整合多模态资源，支持5E教学模型', icon: 'M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777', color: 'bg-cyan-500' },
                      { title: 'Check · 过程性评估', desc: '多维度采集认知过程数据与行为轨迹', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622', color: 'bg-emerald-500' },
                      { title: 'Act · 循证改进', desc: '生成教学洞察，支持循证决策', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10', color: 'bg-amber-500' },
                    ]" :key="idx" class="bg-white rounded-2xl p-8 shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
                      <div class="w-12 h-12 rounded-xl flex items-center justify-center text-white mb-6 shadow-md" :class="item.color">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"></path></svg>
                      </div>
                      <h3 class="text-xl font-bold text-slate-800 mb-3">{{ item.title }}</h3>
                      <p class="text-slate-600 text-sm leading-relaxed">{{ item.desc }}</p>
                    </div>
                  </div>
                </div>

                <!-- Evaluation System Details -->
                <div v-else class="animate-fade-in">
                  <div class="flex flex-col lg:flex-row items-stretch gap-12 lg:gap-16">
                    <!-- Left: Features List -->
                    <div class="lg:w-1/2 space-y-8 flex flex-col justify-center">
                       <div>
                         <div class="inline-flex items-center space-x-2 px-3 py-1 bg-teal-50 rounded-full border border-teal-100 text-teal-700 text-xs font-bold mb-4">
                            <span class="flex h-2 w-2 relative">
                                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                                <span class="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
                            </span>
                            <span>循证教育评价</span>
                         </div>
                         <h2 class="text-3xl md:text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">更科学的<span class="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-emerald-500">增值评价体系</span></h2>
                         <p class="text-lg text-slate-600 leading-relaxed">
                           告别单一的绝对成绩排名。InspireEd 采用先进的增值评估模型，剥离生源基础等外部影响，还原最真实的“教学力”和“进步值”。
                         </p>
                       </div>

                       <div class="grid gap-6">
                         <div v-for="item in [
                           { icon: '📈', title: '关注相对进步', desc: '不看起点看进步。科学计算学生从“入口”到“出口”的实际成长幅度，让每一分努力都被看见。', bg: 'bg-blue-50', border: 'border-blue-100' },
                           { icon: '🧮', title: '多元评价模型', desc: '内置首尾对比、累计增值、线性回归及率指标等多种成熟算法，适应不同学科与学段的评价需求。', bg: 'bg-teal-50', border: 'border-teal-100' },
                           { icon: '🩺', title: '精准诊断改进', desc: '基于增值数据自动生成诊断报告，精准定位薄弱学科与临界生，为分层教学提供循证依据。', bg: 'bg-emerald-50', border: 'border-emerald-100' }
                         ]" :key="item.title" 
                         class="flex gap-5 p-5 bg-white rounded-2xl border hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group"
                         :class="item.border">
                           <div class="flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-3xl shadow-sm transition-transform group-hover:scale-110 group-hover:rotate-3" :class="item.bg">
                             {{ item.icon }}
                           </div>
                           <div>
                             <h4 class="text-lg font-bold text-slate-800 group-hover:text-teal-700 transition-colors">{{ item.title }}</h4>
                             <p class="text-slate-600 mt-2 text-sm leading-relaxed">{{ item.desc }}</p>
                           </div>
                         </div>
                       </div>
                    </div>

                    <!-- Right: Visual Value-Added Report Card -->
                    <div class="lg:w-1/2 flex items-center">
                      <div class="w-full relative group perspective-1000">
                        <!-- Decorative glow -->
                        <div class="absolute -inset-1 bg-gradient-to-r from-teal-500 to-emerald-600 rounded-[2rem] blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                        
                        <!-- Card Container -->
                        <div class="relative bg-white border border-slate-100 rounded-[1.5rem] shadow-2xl overflow-hidden transform transition-transform duration-500 group-hover:rotate-y-2 group-hover:scale-[1.01]">
                          <!-- Card Header -->
                          <div class="px-8 py-6 border-b border-slate-50 bg-slate-50/50 flex justify-between items-center">
                             <div>
                               <div class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">EVALUATION REPORT</div>
                               <div class="font-bold text-slate-800 text-lg">教学增值综合诊断</div>
                             </div>
                             <div class="flex space-x-2">
                               <div class="w-3 h-3 rounded-full bg-red-400"></div>
                               <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
                               <div class="w-3 h-3 rounded-full bg-green-400"></div>
                             </div>
                          </div>

                          <!-- Card Body: 表格式图表 + 效能等级表 -->
                          <div class="p-6 bg-gradient-to-b from-white to-slate-50">
                             <!-- 三列表格：表头 + 柱状图行 -->
                             <div class="overflow-hidden rounded-xl border border-slate-200">
                               <!-- 表头行 -->
                               <div class="grid grid-cols-3 border-b-2 border-slate-200 bg-slate-50">
                                 <div class="border-r border-slate-200 py-3 text-center text-sm font-bold text-slate-600 last:border-r-0">入学基准</div>
                                 <div class="border-r border-slate-200 py-3 text-center text-sm font-bold text-teal-600 last:border-r-0">预期目标</div>
                                 <div class="border-r border-slate-200 py-3 text-center text-sm font-bold text-teal-700 last:border-r-0">实际达成</div>
                               </div>
                               <!-- 数据行：数值 + 柱状图 -->
                               <div class="grid grid-cols-3 min-h-[140px]">
                                 <!-- 列1：入学基准 -->
                                 <div class="flex flex-col items-center border-r border-slate-200 p-4 group/bar last:border-r-0">
                                   <div class="mb-2 text-sm font-bold text-slate-500">75.0</div>
                                   <div class="relative w-full flex-1 min-h-[90px] flex flex-col justify-end">
                                     <div class="w-full bg-slate-200 rounded-t-md h-[40%] group-hover/bar:bg-slate-300 transition-colors"></div>
                                   </div>
                                 </div>
                                 <!-- 列2：预期目标 -->
                                 <div class="flex flex-col items-center border-r border-slate-200 p-4 group/bar last:border-r-0">
                                   <div class="mb-2 text-sm font-bold text-teal-400">82.5</div>
                                   <div class="relative w-full flex-1 min-h-[90px] flex flex-col justify-end">
                                     <div class="w-full border-2 border-dashed border-teal-200 bg-teal-50/50 rounded-t-md h-[60%]"></div>
                                   </div>
                                 </div>
                                 <!-- 列3：实际达成 + 增值 -->
                                 <div class="flex flex-col items-center border-r border-slate-200 p-4 group/bar last:border-r-0">
                                   <div class="mb-2 flex flex-col items-center gap-1">
                                     <span class="inline-block rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-700">+12.5 增值</span>
                                     <span class="text-sm font-bold text-teal-700">87.5</span>
                                   </div>
                                   <div class="relative w-full flex-1 min-h-[90px] flex flex-col justify-end">
                                     <div class="w-full bg-teal-500 rounded-b-sm h-[60%] opacity-90"></div>
                                     <div class="w-full bg-gradient-to-t from-teal-400 to-emerald-500 rounded-t-md h-[25%] shadow shadow-emerald-500/30 animate-pulse-slow"></div>
                                   </div>
                                 </div>
                               </div>
                             </div>

                             <!-- 教学效能等级：小表格 -->
                             <div class="mt-6 overflow-hidden rounded-xl border border-slate-200">
                               <table class="w-full text-sm">
                                 <tbody>
                                   <tr class="border-b border-slate-200">
                                     <td class="bg-slate-50/80 px-4 py-3 font-medium text-slate-600 w-[45%]">教学效能等级</td>
                                     <td class="px-4 py-3 font-bold text-green-700"><span class="rounded bg-green-100 px-2 py-0.5">A+ 卓越</span></td>
                                   </tr>
                                   <tr>
                                     <td colspan="2" class="px-4 py-3">
                                       <div class="mb-2 h-2 w-full overflow-hidden rounded-full bg-slate-200">
                                         <div class="h-full w-[92%] rounded-full bg-gradient-to-r from-emerald-400 to-green-500" style="box-shadow: 0 0 8px rgba(16, 185, 129, 0.35);"></div>
                                       </div>
                                       <p class="text-right text-xs text-slate-400">超越 92% 的同类学校</p>
                                     </td>
                                   </tr>
                                 </tbody>
                               </table>
                             </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </section>
        </div>
      </transition>

      <!-- Scene 2: Login Form (Overlay Mode) -->
      <transition
        enter-active-class="transition duration-500 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition duration-300 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div v-if="showLoginForm" class="flex-grow flex items-center justify-center p-4 relative min-h-[calc(100vh-80px)]">
          <!-- Background Decoration for Login -->
          <div class="absolute inset-0 overflow-hidden pointer-events-none">
            <div class="absolute -top-[20%] -right-[10%] w-[70vh] h-[70vh] rounded-full bg-gradient-to-br from-emerald-200/30 to-teal-200/30 blur-3xl"></div>
            <div class="absolute -bottom-[20%] -left-[10%] w-[70vh] h-[70vh] rounded-full bg-gradient-to-br from-teal-200/30 to-emerald-200/30 blur-3xl"></div>
          </div>

          <div class="w-full max-w-md bg-white/90 backdrop-blur-xl rounded-3xl shadow-2xl p-8 md:p-10 border border-white/50 relative z-10">
            <div class="text-center mb-8">
              <h2 class="text-3xl font-extrabold text-slate-900 tracking-tight">
                {{ isLogin ? '欢迎回来' : '创建账户' }}
              </h2>
              <p class="text-slate-500 mt-2 text-sm">
                {{ isLogin ? '登录到您的 InspireEd 账户' : '注册新账户开始学习之旅' }}
              </p>
            </div>

            <form class="space-y-5" @submit.prevent="handleSubmit">
              <div v-if="!isLogin" class="space-y-1">
                <label class="block text-sm font-medium text-slate-700 ml-1">邮箱地址</label>
                <input
                  v-model="form.email"
                  type="email"
                  required
                  class="block w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 focus:bg-white transition-all duration-200 outline-none"
                  placeholder="your@email.com"
                />
              </div>

              <div class="space-y-1">
                <label class="block text-sm font-medium text-slate-700 ml-1">用户名</label>
                <input
                  v-model="form.username"
                  type="text"
                  required
                  class="block w-full px-4 py-3 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 focus:bg-white transition-all duration-200 outline-none"
                  placeholder="请输入用户名"
                />
              </div>

              <div class="space-y-1">
                <label class="block text-sm font-medium text-slate-700 ml-1">密码</label>
                <div class="relative">
                  <input
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    class="block w-full px-4 py-3 pr-12 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 focus:bg-white transition-all duration-200 outline-none"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 focus:outline-none transition-colors"
                  >
                    <svg v-if="showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" /></svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                  </button>
                </div>
              </div>

              <div v-if="error" class="flex items-start p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600 animate-shake">
                <svg class="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>{{ error }}</span>
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-3.5 px-4 rounded-xl text-white font-bold text-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:shadow-emerald-500/40 transform hover:-translate-y-0.5 active:translate-y-0"
              >
                <span v-if="loading" class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  处理中...
                </span>
                <span v-else>{{ isLogin ? '登 录' : '注 册' }}</span>
              </button>

              <div class="text-center mt-6 space-y-3">
                <button
                  type="button"
                  @click="toggleMode"
                  class="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors hover:underline"
                >
                  {{ isLogin ? '还没有账户？立即注册' : '已有账户？立即登录' }}
                </button>
                <div class="pt-3 border-t border-slate-100">
                  <RouterLink
                    to="/guest"
                    class="inline-flex flex-col items-center gap-0.5 text-sm text-slate-500 hover:text-emerald-600 transition-colors sm:inline-flex sm:flex-row sm:gap-1.5"
                  >
                    <span class="font-medium">访客观摩</span>
                    <span class="text-slate-400 text-xs">无需登录 · 使用课堂接入码</span>
                  </RouterLink>
                </div>
              </div>
            </form>
          </div>
        </div>
      </transition>
    </main>

    <!-- Footer + 开发者信息 -->
    <footer class="border-t border-slate-800 bg-slate-900 py-12 text-white">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col items-center justify-between gap-8 md:flex-row">
          <div class="flex items-center space-x-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-500">
              <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            </div>
            <span class="text-xl font-bold tracking-tight">InspireEd</span>
          </div>
          <div class="text-sm text-slate-400">© 2025 InspireEd. Evidence-based Learning & Teaching Platform.</div>
        </div>
        <address class="mt-6 not-italic border-t border-slate-700/60 pt-6 text-center text-sm text-slate-400 md:text-left">
          开发者：广东省开平市教师发展中心 廖作东 · 邮箱
          <a
            href="mailto:382241106@qq.com"
            aria-label="发送邮件至 382241106@qq.com"
            class="inline-flex cursor-pointer items-center gap-1.5 text-slate-300 underline decoration-slate-500/60 decoration-1 underline-offset-2 transition-colors duration-200 hover:text-emerald-400 hover:decoration-emerald-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 focus-visible:decoration-emerald-400"
          >
            <svg class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
            382241106@qq.com
          </a>
        </address>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { authService } from '../services/auth'
import { UserRole } from '../types/user'
import { libraryService } from '../services/library'

const router = useRouter()
const userStore = useUserStore()

const showLoginForm = ref(false)
const currentSystem = ref<'learning' | 'evaluation'>('learning')
const isLogin = ref(true)
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const htmlResourceCount = ref<number | null>(null)
const lessonCount = ref<number | null>(null)
const isScrolled = ref(false)

const form = ref({
  email: '',
  username: '',
  password: '',
})

// Handle Scroll for Header Glass Effect
function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function toggleMode() {
  isLogin.value = !isLogin.value
  error.value = ''
  showPassword.value = false
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

      // 检查用户是否激活
      if (!user.is_active) {
        error.value = '用户未激活，请联系管理员'
        userStore.logout()
        return
      }

      // 根据角色跳转（支持字符串和枚举两种格式）
      const userRole = user.role?.toLowerCase?.() || user.role
      let targetPath = ''
      if (userRole === UserRole.ADMIN || userRole === 'admin') {
        targetPath = '/admin'
      } else if (userRole === UserRole.DISTRICT_ADMIN || userRole === 'district_admin') {
        targetPath = '/district-admin/exam-management'
      } else if (userRole === UserRole.SCHOOL_ADMIN || userRole === 'school_admin') {
        targetPath = '/school-admin'
      } else if (userRole === UserRole.TEACHER || userRole === 'teacher') {
        targetPath = '/teacher'
      } else if (userRole === UserRole.STUDENT || userRole === 'student') {
        targetPath = '/student'
      } else if (userRole === UserRole.RESEARCHER || userRole === 'researcher') {
        targetPath = '/researcher'
      } else {
        error.value = `用户角色配置错误（当前角色：${user.role}），请联系管理员`
        console.error('Unknown user role:', user.role, user)
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
    console.error('Login error:', err)
    // 提取详细的错误信息
    let errorMessage = '操作失败，请重试'
    if (err.response?.data?.detail) {
      errorMessage = err.response.data.detail
    } else if (err.message) {
      errorMessage = err.message
    }
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

// 获取资源库统计信息
async function loadResourceStatistics() {
  try {
    const stats = await libraryService.getPublicStatistics()
    htmlResourceCount.value = stats.html_resource_count
    lessonCount.value = stats.lesson_count
  } catch (error) {
    console.error('Failed to load resource statistics:', error)
    // 如果获取失败，显示默认值
    htmlResourceCount.value = 200
    lessonCount.value = 500
  }
}

onMounted(() => {
  loadResourceStatistics()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Custom animations */
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animate-blob {
  animation: blob 7s infinite;
}
.animation-delay-2000 {
  animation-delay: 2s;
}
.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
@keyframes shake {
  10%, 90% { transform: translate3d(-1px, 0, 0); }
  20%, 80% { transform: translate3d(2px, 0, 0); }
  30%, 50%, 70% { transform: translate3d(-4px, 0, 0); }
  40%, 60% { transform: translate3d(4px, 0, 0); }
}
.animate-tilt {
  animation: tilt 10s infinite linear;
}
@keyframes tilt {
  0%, 50%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(0.5deg);
  }
  75% {
    transform: rotate(-0.5deg);
  }
}
@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}
.animate-pulse-slow {
  animation: pulse-slow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.perspective-1000 {
  perspective: 1000px;
}
.rotate-y-2 {
  transform: rotateY(2deg);
}
</style>