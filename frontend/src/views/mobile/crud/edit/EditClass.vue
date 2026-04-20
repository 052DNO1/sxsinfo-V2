<template>
  <div class="mobile-page">
    <van-nav-bar title="编辑课表" left-arrow @click-left="goBack">
      <template #right><van-icon name="home-o" size="20" color="#4F6EF7" @click="goHome" /></template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--sunset">
        <div class="form-hero-icon"><van-icon name="edit" size="28" /></div>
        <h2>编辑课表</h2>
        <p>修改课程时间与安排</p>
      </div>

      <van-skeleton v-if="loading" :row="5" animated />

      <van-form v-else @submit="handleSubmit">
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label"><span>🏫</span> 资源分配</div>
          <van-cell-group inset>
            <van-field v-model="laboratoryText" is-link readonly label="实训室" placeholder="请选择实训室" />
            <van-field v-model="teacherText" is-link readonly label="任课教师" placeholder="请选择任课教师" @click="showTeacherPicker = true" />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label"><span>⏰</span> 时间安排</div>
          <van-cell-group inset>
            <van-field v-model="weekdayText" is-link readonly label="星期" required @click="showWeekdayPicker = true" />
            <van-field v-model="timeSlotText" is-link readonly label="节次" required @click="showTimeSlotPicker = true" />
            <van-field v-model="formData.weeks" label="周次" placeholder="如：1-16" clearable />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label"><span>📚</span> 课程信息</div>
          <van-cell-group inset>
            <van-field v-model="formData.class_name" label="班级" required clearable />
            <van-field v-model="formData.course_name" label="课程名称" required clearable />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up">
          <div class="section-label"><span>📝</span> 其他信息</div>
          <van-cell-group inset>
            <van-field v-model="formData.note" rows="3" autosize type="textarea" label="备注" placeholder="请输入备注" />
          </van-cell-group>
        </div>

        <div class="form-actions"><van-button type="primary" block round size="large" :loading="submitting" native-type="submit" icon="success">保存修改</van-button></div>
      </van-form>
    </div>

    <van-popup v-model:show="showWeekdayPicker" position="bottom" round><van-picker title="选择星期" :columns="weekdayOptions" @confirm="(o)=>{formData.weekday=o.selectedValues[0];showWeekdayPicker=false}" @cancel="showWeekdayPicker=false"/></van-popup>
    <van-popup v-model:show="showTimeSlotPicker" position="bottom" round><van-picker title="选择节次" :columns="timeSlotOptions" @confirm="(o)=>{formData.time_slot=o.selectedValues[0];showTimeSlotPicker=false}" @cancel="showTimeSlotPicker=false"/></van-popup>
    <van-popup v-model:show="showTeacherPicker" position="bottom" round><van-picker title="选择教师" :columns="teacherOptions" @confirm="(o)=>{formData.teacher_id=o.selectedValues[0];showTeacherPicker=false}" @cancel="showTeacherPicker=false"/></van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { scheduleService, userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const formData = ref({ laboratory_id: '', weekday: 1, time_slot: '1-2', weeks: '', class_name: '', course_name: '', teacher_id: null, note: '' })
const showWeekdayPicker = ref(false)
const showTimeSlotPicker = ref(false)
const showTeacherPicker = ref(false)
const teacherList = ref([])
const laboratoryName = ref('')

const weekdayOptions = [{ text:'星期一',value:1 },{ text:'星期二',value:2 },{ text:'星期三',value:3 },{ text:'星期四',value:4 },{ text:'星期五',value:5 },{ text:'星期六',value:6 },{ text:'星期日',value:7 }]
const timeSlotOptions = [{ text:'1-2节',value:'1-2' },{ text:'3-4节',value:'3-4' },{ text:'5-6节',value:'5-6' },{ text:'7-8节',value:'7-8' },{ text:'9-10节',value:'9-10' },{ text:'1-4节',value:'1-4' },{ text:'5-8节',value:'5-8' }]
const teacherOptions = computed(() => [{text:'不指定',value:''},...teacherList.value.map(t => ({text:t.nickname||t.username,value:t.id}))])
const weekdayText = computed(() => weekdayOptions.find(o=>o.value===formData.value.weekday)?.text||'')
const timeSlotText = computed(() => timeSlotOptions.find(o=>o.value===formData.value.time_slot)?.text||'')
const laboratoryText = computed(() => laboratoryName.value)
const teacherText = computed(() => teacherList.value.find(t=>t.id===formData.value.teacher_id)?.nickname||teacherList.value.find(t=>t.id===formData.value.teacher_id)?.username||'不指定')

onMounted(async () => {
  loading.value = true
  try {
    const [scheduleRes, teachersRes] = await Promise.all([scheduleService.get(route.params.id), userService.list({nopage:true})])
    const d = scheduleRes?.data || scheduleRes || {}
    teacherList.value = teachersRes?.list || teachersRes?.data?.list || []
    Object.assign(formData.value, { laboratory_id:d.laboratory?.id||d.laboratory_id||'', weekday:d.weekday||1, time_slot:d.time_slot||'1-2', weeks:d.weeks||'', class_name:d.class_name||'', course_name:d.course_name||'', teacher_id:d.teacher?.id||d.teacher_id||null, note:d.note||'' })
    laboratoryName.value = d.laboratory_name || d.laboratory?.name || ''
  } catch (e) { showError('加载数据失败') }
  finally { loading.value = false }
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    await scheduleService.update(route.params.id, { laboratory: formData.value.laboratory_id, weekday: formData.value.weekday, time_slot: formData.value.time_slot, weeks: formData.value.weeks, class_name: formData.value.class_name, course_name: formData.value.course_name, teacher: formData.value.teacher_id||null, note: formData.value.note })
    showSuccess('修改成功'); setTimeout(()=>smartBack(),1500)
  } catch (e) { showError(e.message||'修改失败') }
  finally { submitting.value = false }
}
</script>

<style scoped>
.form-hero--sunset { background: #E8FAF0; }
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #E8FAF0; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #1ABC9C; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: rgba(255,255,255,0.8); }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>