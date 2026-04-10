/**
 * 钢管回弹智能补偿系统 - Node.js 后端服务
 * 兼容版本（无需 Python）
 */
import express from 'express';
import cors from 'cors';
import { randomUUID } from 'crypto';

const app = express();
const PORT = 8000;

// 中间件
app.use(cors());
app.use(express.json());

// ==================== 内存存储 ====================
const history = [];

// 设备状态
let deviceState = {
  device_id: 'SIM-001',
  device_status: 'idle',
  online: true,
  current_task: null,
  current_angle: 0,
  actual_angle: 0,
  deviation: 0,
  last_heartbeat: new Date().toISOString()
};

// 任务执行中的标记
let runningTaskTimeout = null;

// ==================== 规则引擎 ====================
const MATERIAL_OFFSET = {
  '普通钢': 2.0,
  '高强钢': 3.0,
  '不锈钢': 2.5,
  '铝合金': 1.5
};

function calculateRecommendation(diameter, thickness, material, targetAngle) {
  // 基础补偿
  const baseOffset = MATERIAL_OFFSET[material] || 2.0;
  
  // 壁厚修正
  let thicknessAdjustment = 0;
  if (thickness > 10) thicknessAdjustment = -0.5;
  else if (thickness < 3) thicknessAdjustment = 0.5;
  
  // 管径修正
  let diameterAdjustment = 0;
  if (diameter > 200) diameterAdjustment = -0.3;
  
  // 总补偿
  const totalOffset = baseOffset + thicknessAdjustment + diameterAdjustment;
  const recommendedAngle = targetAngle + totalOffset;
  
  // 生成说明
  const parts = [`基于${material}材质，基础补偿值为+${baseOffset}°`];
  if (thicknessAdjustment !== 0) {
    const adjText = thicknessAdjustment > 0 ? '增加' : '减少';
    parts.push(`壁厚${thickness}mm，${adjText}补偿${Math.abs(thicknessAdjustment)}°`);
  }
  if (diameterAdjustment !== 0) {
    parts.push(`管径${diameter}mm较大，减少补偿${Math.abs(diameterAdjustment)}°`);
  }
  parts.push(`综合补偿值为${totalOffset >= 0 ? '+' : ''}${totalOffset.toFixed(2)}°`);
  
  return {
    recommended_angle: Math.round(recommendedAngle * 100) / 100,
    recommended_offset: Math.round(totalOffset * 100) / 100,
    explanation: parts.join('。'),
    timestamp: new Date().toISOString()
  };
}

// ==================== API 路由 ====================

// 健康检查
app.get('/', (req, res) => {
  res.json({
    name: '钢管回弹智能补偿系统 API (Node.js 版)',
    version: '0.1.0',
    status: 'running'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// 1. 推荐参数
app.post('/api/recommend', (req, res) => {
  try {
    const { diameter, thickness, material, target_angle } = req.body;
    
    // 参数验证
    if (!diameter || !thickness || !material || target_angle === undefined) {
      return res.status(400).json({ code: 1, message: '缺少必要参数', data: null });
    }
    
    const result = calculateRecommendation(diameter, thickness, material, target_angle);
    
    res.json({
      code: 0,
      message: 'success',
      data: result
    });
  } catch (error) {
    res.status(500).json({ code: 1, message: error.message, data: null });
  }
});

// 2. 获取设备状态
app.get('/api/device/status', (req, res) => {
  // 更新心跳时间
  deviceState.last_heartbeat = new Date().toISOString();
  
  res.json({
    code: 0,
    message: 'success',
    data: deviceState
  });
});

// 3. 提交任务
app.post('/api/device/submit', (req, res) => {
  try {
    const { diameter, thickness, material, target_angle, recommended_angle, recommended_offset } = req.body;
    
    // 检查设备状态
    if (!deviceState.online) {
      return res.status(400).json({ code: 1, message: '设备离线，无法提交任务', data: null });
    }
    
    if (deviceState.device_status === 'running') {
      return res.status(400).json({ code: 1, message: '设备正在执行任务，请等待完成', data: null });
    }
    
    // 生成任务ID
    const taskId = `TASK-${randomUUID().slice(0, 8).toUpperCase()}`;
    
    // 创建历史记录
    const record = {
      id: taskId,
      input_params: { diameter, thickness, material, target_angle },
      recommend_params: {
        recommended_angle,
        recommended_offset,
        explanation: `基于${material}材质的推荐`
      },
      created_at: new Date().toISOString(),
      execute_result: null,
      completed_at: null
    };
    history.unshift(record);
    
    // 更新设备状态
    deviceState.device_status = 'running';
    deviceState.current_task = taskId;
    deviceState.current_angle = recommended_angle;
    deviceState.actual_angle = 0;
    deviceState.deviation = 0;
    
    // 模拟任务执行（3-8秒后完成）
    const executionTime = 3000 + Math.random() * 5000;
    
    if (runningTaskTimeout) clearTimeout(runningTaskTimeout);
    
    runningTaskTimeout = setTimeout(() => {
      // 模拟实际角度误差（±0.5度）
      const error = (Math.random() - 0.5);
      deviceState.actual_angle = Math.round((recommended_angle + error) * 100) / 100;
      deviceState.deviation = Math.round(error * 100) / 100;
      deviceState.device_status = 'completed';
      
      // 更新历史记录
      const recordIndex = history.findIndex(r => r.id === taskId);
      if (recordIndex >= 0) {
        history[recordIndex].execute_result = {
          actual_angle: deviceState.actual_angle,
          deviation: deviceState.deviation,
          final_status: 'completed'
        };
        history[recordIndex].completed_at = new Date().toISOString();
      }
      
      console.log(`[${new Date().toLocaleTimeString()}] 任务 ${taskId} 已完成`);
    }, executionTime);
    
    res.json({
      code: 0,
      message: 'success',
      data: {
        task_id: taskId,
        status: 'running',
        message: `任务 ${taskId} 已开始执行`
      }
    });
    
  } catch (error) {
    res.status(500).json({ code: 1, message: error.message, data: null });
  }
});

// 4. 获取历史记录
app.get('/api/history', (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  res.json({
    code: 0,
    message: 'success',
    data: history.slice(0, limit)
  });
});

// 启动服务
app.listen(PORT, () => {
  console.log('='.repeat(50));
  console.log('🚀 钢管回弹智能补偿系统后端服务已启动');
  console.log(`📡 服务地址: http://localhost:${PORT}`);
  console.log(`📚 API 文档: http://localhost:${PORT}/api/docs`);
  console.log('='.repeat(50));
});
