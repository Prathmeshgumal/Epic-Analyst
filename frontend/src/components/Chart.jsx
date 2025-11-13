import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './Chart.css'

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe', '#43e97b', '#38f9d7', '#fa709a', '#fee140']

function Chart({ data, chartConfig }) {
  const chartData = useMemo(() => {
    if (!data || !chartConfig || !chartConfig.should_visualize) return null
    
    const { chart_type, x_axis, y_axis } = chartConfig
    
    if (!x_axis || !y_axis) return null
    
    // Transform data for charts
    return data.map((row, index) => {
      const xValue = row[x_axis]
      let yValue = row[y_axis]
      
      // Try to parse as number
      if (typeof yValue === 'string') {
        yValue = parseFloat(yValue) || 0
      } else if (yValue == null) {
        yValue = 0
      }
      
      const result = {
        name: String(xValue),
        value: yValue,
        originalIndex: index
      }
      
      // For scatter charts, also include x as numeric value
      if (chart_type === 'scatter') {
        let xNum = xValue
        if (typeof xValue === 'string') {
          xNum = parseFloat(xValue) || 0
        }
        result.x = xNum
      }
      
      return result
    })
  }, [data, chartConfig])
  
  if (!chartConfig || !chartConfig.should_visualize || !chartData) {
    return null
  }
  
  const { chart_type, x_axis, y_axis } = chartConfig
  
  // Render appropriate chart type
  const renderChart = () => {
    switch (chart_type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis 
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-primary)'
                }}
              />
              <Legend 
                wrapperStyle={{ color: 'var(--text-primary)' }}
              />
              <Bar 
                dataKey="value" 
                fill="#667eea" 
                name={y_axis}
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )
      
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis 
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-primary)'
                }}
              />
              <Legend 
                wrapperStyle={{ color: 'var(--text-primary)' }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#667eea" 
                strokeWidth={2}
                dot={{ fill: '#667eea', r: 4 }}
                activeDot={{ r: 6 }}
                name={y_axis}
              />
            </LineChart>
          </ResponsiveContainer>
        )
      
      case 'pie':
        const pieData = chartData.slice(0, 10) // Limit to 10 categories
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={120}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-primary)'
                }}
              />
              <Legend 
                wrapperStyle={{ color: 'var(--text-primary)' }}
              />
            </PieChart>
          </ResponsiveContainer>
        )
      
      case 'area':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#667eea" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#667eea" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={100}
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis 
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-primary)'
                }}
              />
              <Legend 
                wrapperStyle={{ color: 'var(--text-primary)' }}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#667eea" 
                fillOpacity={1} 
                fill="url(#colorValue)" 
                name={y_axis}
              />
            </AreaChart>
          </ResponsiveContainer>
        )
      
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
              <XAxis 
                type="number"
                dataKey="x"
                name={x_axis}
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <YAxis 
                type="number"
                dataKey="value"
                name={y_axis}
                stroke="var(--text-secondary)"
                tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                contentStyle={{
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  color: 'var(--text-primary)'
                }}
              />
              <Scatter name="Data" data={chartData} fill="#667eea" />
            </ScatterChart>
          </ResponsiveContainer>
        )
      
      default:
        return null
    }
  }
  
  return (
    <div className="chart-container">
      <div className="chart-title">
        {chartConfig.explanation && (
          <p className="chart-explanation">{chartConfig.explanation}</p>
        )}
      </div>
      {renderChart()}
    </div>
  )
}

export default Chart

