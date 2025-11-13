import { useState } from 'react'
import './DataTable.css'

function DataTable({ data, columns, rowCount }) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  if (!data || data.length === 0) {
    return null
  }

  // Get columns from data if not provided
  const tableColumns = columns && columns.length > 0 
    ? columns 
    : Object.keys(data[0] || {})

  // Sort data
  const sortedData = [...data]
  if (sortConfig.key) {
    sortedData.sort((a, b) => {
      const aVal = a[sortConfig.key]
      const bVal = b[sortConfig.key]
      
      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
      }
      
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      
      if (sortConfig.direction === 'asc') {
        return aStr.localeCompare(bStr)
      } else {
        return bStr.localeCompare(aStr)
      }
    })
  }

  // Paginate data
  const totalPages = Math.ceil(sortedData.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const paginatedData = sortedData.slice(startIndex, endIndex)

  function handleSort(key) {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  function formatValue(value) {
    if (value === null || value === undefined) {
      return <span className="null-value">null</span>
    }
    if (typeof value === 'boolean') {
      return value ? '✓' : '✗'
    }
    return String(value)
  }

  return (
    <div className="data-table-container">
      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              {tableColumns.map((column) => (
                <th
                  key={column}
                  onClick={() => handleSort(column)}
                  className={sortConfig.key === column ? 'sorted' : ''}
                >
                  <div className="th-content">
                    <span>{column}</span>
                    {sortConfig.key === column && (
                      <span className="sort-icon">
                        {sortConfig.direction === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((row, index) => (
              <tr key={index}>
                {tableColumns.map((column) => (
                  <td key={column}>{formatValue(row[column])}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="table-footer">
        <div className="table-info">
          Showing {startIndex + 1}-{Math.min(endIndex, sortedData.length)} of {sortedData.length} rows
          {rowCount && rowCount !== sortedData.length && ` (Total: ${rowCount})`}
        </div>
        
        {totalPages > 1 && (
          <div className="pagination">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="page-btn"
            >
              ← Prev
            </button>
            <span className="page-info">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="page-btn"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default DataTable

