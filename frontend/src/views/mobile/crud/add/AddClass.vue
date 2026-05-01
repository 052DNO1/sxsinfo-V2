<template>
  <div class="mobile-page">
    <van-nav-bar
      title="添加课表"
      left-arrow
      @click-left="goBack"
    >
      <template #right>
        <van-icon
          name="home-o"
          size="20"
          color="#4F6EF7"
          @click="goHome"
        />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="form-hero form-hero--warm">
        <div class="form-hero-icon">
          <van-icon
            name="calendar-o"
            size="28"
          />
        </div>
        <h2>添加新课表</h2>
        <p>安排课程时间与教室</p>
      </div>

      <van-skeleton
        v-if="loading"
        :row="5"
        animated
      />

      <van-form
        v-else
        @submit="handleSubmit"
      >
        <div class="form-section animate-fade-in-up animate-delay-1">
          <div class="section-label">
            <span>🏫</span> 资源分配
          </div>
          <van-cell-group inset>
            <van-field
              v-model="laboratoryText"
              is-link
              readonly
              label="实训室"
              placeholder="请选择实训室"
              required
              @click="showLabPicker = true"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-2">
          <div class="section-label">
            <span>⏰</span> 时间安排
          </div>
          <van-cell-group inset>
            <van-field
              v-model="weekdayText"
              is-link
              readonly
              label="星期"
              placeholder="请选择星期"
              required
              @click="showWeekdayPicker = true"
            />
            <van-field
              v-model="timeSlotText"
              is-link
              readonly
              label="节次"
              placeholder="请选择节次"
              required
              @click="showTimeSlotPicker = true"
            />
            <van-field
              v-model="formData.weeks"
              label="周次"
              placeholder="如：1-16 或 1,3,5,7"
              clearable
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up animate-delay-3">
          <div class="section-label">
            <span>📚</span> 课程信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.class_name"
              label="班级"
              placeholder="请输入班级名称"
              required
              clearable
              :rules="[{ required: true, message: '请输入班级名称' }]"
            />
            <van-field
              v-model="formData.course_name"
              label="课程名称"
              placeholder="请输入课程名称"
              required
              clearable
              :rules="[{ required: true, message: '请输入课程名称' }]"
            />
            <van-field
              v-model="teacherText"
              is-link
              readonly
              label="任课教师"
              placeholder="请选择任课教师"
              required
              @click="showTeacherPicker = true"
            />
          </van-cell-group>
        </div>

        <div class="form-section animate-fade-in-up">
          <div class="section-label">
            <span>📝</span> 其他信息
          </div>
          <van-cell-group inset>
            <van-field
              v-model="formData.note"
              rows="3"
              autosize
              type="textarea"
              label="备注"
              placeholder="请输入备注"
            />
          </van-cell-group>
        </div>

        <div class="form-actions">
          <van-button
            type="primary"
            block
            round
            size="large"
            :loading="submitting"
            native-type="submit"
            icon="success"
          >
            立即创建
          </van-button>
        </div>
      </van-form>
    </div>

    <van-popup
      v-model:show="showWeekdayPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择星期"
        :columns="weekdayOptions"
        @confirm="onWeekdayConfirm"
        @cancel="showWeekdayPicker = false"
      />
    </van-popup>
    <van-popup
      v-model:show="showTimeSlotPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择节次"
        :columns="timeSlotOptions"
        @confirm="onTimeSlotConfirm"
        @cancel="showTimeSlotPicker = false"
      />
    </van-popup>
    <van-popup
      v-model:show="showLabPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择实训室"
        :columns="labOptions"
        @confirm="onLabConfirm"
        @cancel="showLabPicker = false"
      />
    </van-popup>
    <van-popup
      v-model:show="showTeacherPicker"
      position="bottom"
      round
    >
      <van-picker
        title="选择教师"
        :columns="teacherOptions"
        @confirm="onTeacherConfirm"
        @cancel="showTeacherPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNavigation } from '@/core/utils/routeDecision'
import { scheduleService, labService, userService } from '@/core/services/BaseService'
import { showSuccess, showError } from '@/core/utils/errorHandler'

const route = useRoute()
const router = useRouter()
const { goHome, smartBack } = useNavigation()

const loading = ref(false)
const submitting = ref(false)
const formData = ref({ laboratory_id: '', weekday: 1, time_slot: '1-2', weeks: '', class_name: '', course_name: '', teacher_id: null, note: '' })

const showWeekdayPicker = ref(false)
const showTimeSlotPicker = ref(false)
const showLabPicker = ref(false)
const showTeacherPicker = ref(false)
const labList = ref([])
const teacherList = ref([])

const weekdayOptions = [
  { text: '星期一', value: 1 }, { text: '星期二', value: 2 }, { text: '星期三', value: 3 },
  { text: '星期四', value: 4 }, { text: '星期五', value: 5 }, { text: '星期六', value: 6 }, { text: '星期日', value: 7 }
]
const timeSlotOptions = [
  { text: '1-2节（上午第1-2节）', value: '1-2' }, { text: '3-4节（上午第3-4节）', value: '3-4' },
  { text: '5-6节（下午第1-2节）', value: '5-6' }, { text: '7-8节（下午第3-4节）', value: '7-8' },
  { text: '9-10节（晚上）', value: '9-10' }, { text: '1-4节（上午连课）', value: '1-4' },
  { text: '5-8节（下午连课）', value: '5-8' }, { text: '1-6节（全天）', value: '1-6' }, { text: '1-8节（全天含晚自习）', value: '1-8' }
]

const labOptions = computed(() => labList.value.map(lab => ({ text: `${lab.code || ''} ${lab.name || lab.laboratory_name}`.trim(), value: lab.id })))
const teacherOptions = computed(() => teacherList.value.map(t => ({ text: t.nickname || t.username, value: t.id })))
const weekdayText = computed(() => weekdayOptions.find(o => o.value === formData.value.weekday)?.text || '')
const timeSlotText = computed(() => timeSlotOptions.find(o => o.value === formData.value.time_slot)?.text || formData.value.time_slot)
const laboratoryText = computed(() => { const lab = labList.value.find(l => l.id === formData.value.laboratory_id); return lab ? `${lab.code || ''} ${lab.name || lab.laboratory_name}`.trim() : '' })
const teacherText = computed(() => { const teacher = teacherList.value.find(t => t.id === formData.value.teacher_id); return teacher ? (teacher.nickname || teacher.username) : '' })

const loadData = async () => {
  loading.value = true
  try {
    const [labsRes, teachersRes] = await Promise.all([labService.list({ nopage: true }), userService.list({ nopage: true })])
    labList.value = labsRes?.list || labsRes?.data?.list || []
    teacherList.value = teachersRes?.list || teachersRes?.data?.list || []
    if (route.params.sxsid || route.query.sxsid) formData.value.laboratory_id = parseInt(route.params.sxsid || route.query.sxsid)
    if (route.query.weekday) formData.value.weekday = parseInt(route.query.weekday)
    if (route.query.period) formData.value.time_slot = route.query.period
  } catch (err) { showError('加载数据失败') }
  finally { loading.value = false }
}

const onWeekdayConfirm = ({ selectedOptions }) => { formData.value.weekday = selectedOptions[0].value; showWeekdayPicker.value = false }
const onTimeSlotConfirm = ({ selectedOptions }) => { formData.value.time_slot = selectedOptions[0].value; showTimeSlotPicker.value = false }
const onLabConfirm = ({ selectedOptions }) => { formData.value.laboratory_id = selectedOptions[0].value; showLabPicker.value = false }
const onTeacherConfirm = ({ selectedOptions }) => { formData.value.teacher_id = selectedOptions[0].value; showTeacherPicker.value = false }

const handleSubmit = async () => {
  submitting.value = true
  try {
    await scheduleService.create({ laboratory: formData.value.laboratory_id, weekday: formData.value.weekday, time_slot: formData.value.time_slot, weeks: formData.value.weeks, class_name: formData.value.class_name, course_name: formData.value.course_name, teacher: formData.value.teacher_id, note: formData.value.note })
    showSuccess('创建成功')
    setTimeout(() => smartBack(), 1500)
  } catch (err) { showError(err.message || '创建失败') }
  finally { submitting.value = false }
}
const goBack = () => router.go(-1)

onMounted(() => loadData())
</script>

<style scoped>
.form-hero { background: #F7F8FA; padding: 28px 20px; margin: -12px -16px 20px; text-align: center; border-radius: 0 0 16px 16px; }
.form-hero--warm { background: #E8FAF0; }
.form-hero-icon { width: 60px; height: 60px; border-radius: 50%; background: #E8FAF0; display: flex; align-items: center; justify-content: center; margin: 0 auto 12px; color: #1ABC9C; }
.form-hero h2 { margin: 0 0 6px; font-size: 20px; font-weight: 700; color: #1A1A1A; }
.form-hero p { margin: 0; font-size: 13px; color: #666666; }
.form-section { margin-bottom: 8px; }
.section-label { display: flex; align-items: center; gap: 8px; padding: 10px 16px 6px; font-size: 13px; font-weight: 600; color: var(--mobile-text-secondary); }
.section-label span { font-size: 16px; }
</style>