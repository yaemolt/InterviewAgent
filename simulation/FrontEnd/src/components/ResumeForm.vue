<template>
  <div class="resume-form-container">
    <div class="resume-form">
      <h2 class="form-title">📝 个人简历信息</h2>
      
      <form @submit.prevent="handleSubmit" class="form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>
          <div class="form-row">
            <div class="form-group">
              <label>姓名 *</label>
              <input 
                v-model="resume.name" 
                type="text" 
                placeholder="请输入您的姓名"
                required
              />
            </div>
            <div class="form-group">
              <label>年龄</label>
              <input 
                v-model="resume.age" 
                type="number" 
                placeholder="年龄"
                min="18" max="65"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>联系电话</label>
              <input 
                v-model="resume.phone" 
                type="tel" 
                placeholder="请输入手机号码"
              />
            </div>
            <div class="form-group">
              <label>邮箱</label>
              <input 
                v-model="resume.email" 
                type="email" 
                placeholder="example@email.com"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>居住城市</label>
            <input 
              v-model="resume.location" 
              type="text" 
              placeholder="如：北京、上海、深圳"
            />
          </div>
        </div>

        <!-- 求职意向 -->
        <div class="form-section">
          <h3 class="section-title">求职意向</h3>
          <div class="form-row">
            <div class="form-group">
              <label>期望职位 *</label>
              <select v-model="resume.targetPosition" required>
                <option value="">请选择期望职位</option>
                <option value="前端开发工程师">前端开发工程师</option>
                <option value="后端开发工程师">后端开发工程师</option>
                <option value="全栈开发工程师">全栈开发工程师</option>
                <option value="算法工程师">算法工程师</option>
                <option value="数据分析师">数据分析师</option>
                <option value="产品经理">产品经理</option>
                <option value="UI/UX设计师">UI/UX设计师</option>
                <option value="测试工程师">测试工程师</option>
                <option value="运维工程师">运维工程师</option>
                <option value="项目经理">项目经理</option>
                <option value="其他">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>期望薪资</label>
              <select v-model="resume.expectedSalary">
                <option value="">请选择期望薪资</option>
                <option value="5-8K">5-8K</option>
                <option value="8-12K">8-12K</option>
                <option value="12-18K">12-18K</option>
                <option value="18-25K">18-25K</option>
                <option value="25-35K">25-35K</option>
                <option value="35K以上">35K以上</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 教育背景 -->
        <div class="form-section">
          <h3 class="section-title">教育背景</h3>
          <div class="form-row">
            <div class="form-group">
              <label>学历 *</label>
              <select v-model="resume.education" required>
                <option value="">请选择学历</option>
                <option value="高中">高中</option>
                <option value="大专">大专</option>
                <option value="本科">本科</option>
                <option value="硕士">硕士</option>
                <option value="博士">博士</option>
              </select>
            </div>
            <div class="form-group">
              <label>专业</label>
              <input 
                v-model="resume.major" 
                type="text" 
                placeholder="如：计算机科学与技术"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>毕业院校</label>
              <input 
                v-model="resume.university" 
                type="text" 
                placeholder="请输入毕业院校"
              />
            </div>
            <div class="form-group">
              <label>毕业年份</label>
              <input 
                v-model="resume.graduationYear" 
                type="number" 
                placeholder="2024"
                min="2000" :max="new Date().getFullYear() + 4"
              />
            </div>
          </div>
        </div>

        <!-- 工作经验 -->
        <div class="form-section">
          <h3 class="section-title">工作经验</h3>
          <div class="form-group">
            <label>工作年限</label>
            <select v-model="resume.workExperience">
              <option value="">请选择工作年限</option>
              <option value="应届毕业生">应届毕业生</option>
              <option value="1年以下">1年以下</option>
              <option value="1-3年">1-3年</option>
              <option value="3-5年">3-5年</option>
              <option value="5-10年">5-10年</option>
              <option value="10年以上">10年以上</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>工作经历描述</label>
            <textarea 
              v-model="resume.workDescription" 
              placeholder="请描述您的主要工作经历、职责和成就（可选）"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- 技能特长 -->
        <div class="form-section">
          <h3 class="section-title">技能特长</h3>
          <div class="form-group">
            <label>技术技能</label>
            <textarea 
              v-model="resume.technicalSkills" 
              placeholder="请列出您掌握的编程语言、框架、工具等，如：JavaScript, Vue.js, Python, MySQL..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>其他技能</label>
            <textarea 
              v-model="resume.otherSkills" 
              placeholder="如：外语能力、证书、项目管理经验等"
              rows="2"
            ></textarea>
          </div>
        </div>

        <!-- 项目经验 -->
        <div class="form-section">
          <h3 class="section-title">项目经验</h3>
          <div class="form-group">
            <label>项目经验描述</label>
            <textarea 
              v-model="resume.projectExperience" 
              placeholder="请描述您参与过的重要项目，包括项目背景、您的角色、使用的技术、取得的成果等"
              rows="4"
            ></textarea>
          </div>
        </div>

        <!-- 自我评价 -->
        <div class="form-section">
          <h3 class="section-title">自我评价</h3>
          <div class="form-group">
            <label>个人优势</label>
            <textarea 
              v-model="resume.selfEvaluation" 
              placeholder="请简述您的个人优势、性格特点、职业目标等"
              rows="3"
            ></textarea>
          </div>
        </div>

        <!-- 提交按钮 -->
        <div class="form-actions">
          <button type="button" @click="$emit('cancel')" class="btn-cancel">
            取消
          </button>
          <button type="submit" :disabled="loading" class="btn-submit">
            {{ loading ? '提交中...' : '提交简历并开始面试' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const resume = reactive({
  // 基本信息
  name: '',
  age: '',
  phone: '',
  email: '',
  location: '',
  
  // 求职意向
  targetPosition: '',
  expectedSalary: '',
  
  // 教育背景
  education: '',
  major: '',
  university: '',
  graduationYear: '',
  
  // 工作经验
  workExperience: '',
  workDescription: '',
  
  // 技能特长
  technicalSkills: '',
  otherSkills: '',
  
  // 项目经验
  projectExperience: '',
  
  // 自我评价
  selfEvaluation: ''
})

const handleSubmit = () => {
  // 验证必填字段
  if (!resume.name || !resume.targetPosition || !resume.education) {
    alert('请填写必填字段（姓名、期望职位、学历）')
    return
  }
  
  emit('submit', { ...resume })
}
</script>

<style scoped>
.resume-form-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.resume-form {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.form-title {
  text-align: center;
  color: #333;
  margin-bottom: 2rem;
  font-size: 1.8rem;
  font-weight: 700;
}

.form-section {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-title {
  color: #667eea;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #667eea;
  display: inline-block;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 500;
  color: #555;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
}

.btn-cancel,
.btn-submit {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-cancel {
  background: #f8f9fa;
  color: #6c757d;
  border: 2px solid #dee2e6;
}

.btn-cancel:hover {
  background: #e9ecef;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

@media (max-width: 768px) {
  .resume-form {
    padding: 1.5rem;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
}
</style> 