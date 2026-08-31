import {
  Alert,
  Button,
  Card,
  Descriptions,
  Divider,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Space,
  Spin,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from "antd"

import type { ColumnsType } from "antd/es/table"

import {
  CalculatorOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
} from "@ant-design/icons"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  calculateSalary,
  createDeduction,
  createSalary,
  deleteDeduction,
  deleteSalary,
  getDeductions,
  getSalaries,
  updateDeduction,
  updateSalary,
} from "../../api/payroll"

import type {
  EmployeeSalary,
  PayrollCalculation,
  PayrollDeduction,
} from "../../types/payroll"

import { getEmployees } from "../../api/employees"

import type { Employee } from "../../types/employee"

const { Title, Text } = Typography

/* =========================================================
   Options
========================================================= */

const deductionTypeOptions = [
  {
    label: "بیمه",
    value: "insurance",
  },
  {
    label: "مالیات",
    value: "tax",
  },
  {
    label: "علی‌الحساب",
    value: "advance",
  },
  {
    label: "وام",
    value: "loan",
  },
  {
    label: "غیبت",
    value: "absence",
  },
  {
    label: "سایر",
    value: "other",
  },
]

const monthOptions = Array.from(
  { length: 12 },
  (_, index) => ({
    label: `ماه ${index + 1}`,
    value: index + 1,
  }),
)

/* =========================================================
   Helpers
========================================================= */

function formatMoney(
  value: string | number,
): string {
  const number =
    typeof value === "number"
      ? value
      : Number(value)

  if (Number.isNaN(number)) {
    return String(value)
  }

  return new Intl.NumberFormat(
    "fa-IR",
  ).format(number)
}

/* =========================================================
   Salary Form
========================================================= */

interface SalaryFormValues {
  employee: number
  year: number
  month: number
  monthly_wage: number
  worker_food_allowance: number
  housing_allowance: number
  marriage_allowance: number
  notes?: string
}

/* =========================================================
   Deduction Form
========================================================= */

interface DeductionFormValues {
  salary: number
  deduction_type:
    | "insurance"
    | "tax"
    | "advance"
    | "loan"
    | "absence"
    | "other"
  amount: number
  description?: string
}

/* =========================================================
   Page
========================================================= */

export default function PayrollPage() {
  /* =======================================================
     Forms
  ======================================================= */

  const [salaryForm] =
    Form.useForm<SalaryFormValues>()

  const [deductionForm] =
    Form.useForm<DeductionFormValues>()

  /* =======================================================
     Main Data
  ======================================================= */

  const [salaries, setSalaries] =
    useState<EmployeeSalary[]>([])

  const [deductions, setDeductions] =
    useState<PayrollDeduction[]>([])

  const [employees, setEmployees] =
    useState<Employee[]>([])

  /* =======================================================
     Loading / Errors
  ======================================================= */

  const [loading, setLoading] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [deductionSaving, setDeductionSaving] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  /* =======================================================
     Salary Filters
  ======================================================= */

  const [
    salaryEmployeeFilter,
    setSalaryEmployeeFilter,
  ] = useState<number | undefined>(
    undefined,
  )

  const [salaryYear, setSalaryYear] =
    useState<number | undefined>(
      undefined,
    )

  const [salaryMonth, setSalaryMonth] =
    useState<number | undefined>(
      undefined,
    )

  /* =======================================================
     Deduction Filters
  ======================================================= */

  const [
    deductionSalaryFilter,
    setDeductionSalaryFilter,
  ] = useState<number | undefined>(
    undefined,
  )

  const [
    deductionTypeFilter,
    setDeductionTypeFilter,
  ] = useState<
    PayrollDeduction["deduction_type"] |
    undefined
  >(undefined)

  /* =======================================================
     Salary Modal
  ======================================================= */

  const [
    salaryModalOpen,
    setSalaryModalOpen,
  ] = useState(false)

  const [
    editingSalary,
    setEditingSalary,
  ] = useState<EmployeeSalary | null>(
    null,
  )

  /* =======================================================
     Salary Details
  ======================================================= */

  const [
    detailsModalOpen,
    setDetailsModalOpen,
  ] = useState(false)

  const [
    selectedSalary,
    setSelectedSalary,
  ] = useState<EmployeeSalary | null>(
    null,
  )

  /* =======================================================
     Calculation Modal
  ======================================================= */

  const [
    calculationModalOpen,
    setCalculationModalOpen,
  ] = useState(false)

  const [
    calculation,
    setCalculation,
  ] = useState<PayrollCalculation | null>(
    null,
  )

  const [
    calculationLoading,
    setCalculationLoading,
  ] = useState(false)

  /* =======================================================
     Deduction Modal
  ======================================================= */

  const [
    deductionModalOpen,
    setDeductionModalOpen,
  ] = useState(false)

  const [
    editingDeduction,
    setEditingDeduction,
  ] = useState<PayrollDeduction | null>(
    null,
  )

  /* =======================================================
     Deduction Details
  ======================================================= */

  const [
    deductionDetailsModalOpen,
    setDeductionDetailsModalOpen,
  ] = useState(false)

  const [
    selectedDeduction,
    setSelectedDeduction,
  ] = useState<PayrollDeduction | null>(
    null,
  )

  /* =======================================================
     Maps
  ======================================================= */

  const employeeMap = useMemo(
    () =>
      new Map(
        employees.map((employee) => [
          employee.id,
          employee,
        ]),
      ),
    [employees],
  )

  const salaryMap = useMemo(
    () =>
      new Map(
        salaries.map((salary) => [
          salary.id,
          salary,
        ]),
      ),
    [salaries],
  )

  /* =======================================================
     Helpers
  ======================================================= */

  const getEmployeeName = (
    employeeId: number,
  ) => {
    const employee =
      employeeMap.get(employeeId)

    if (!employee) {
      return `کارمند #${employeeId}`
    }

    return `${employee.first_name} ${employee.last_name}`
  }

  const getSalaryPeriod = (
    salary: EmployeeSalary,
  ) =>
    `${salary.year}/${String(
      salary.month,
    ).padStart(2, "0")}`

  /* =======================================================
     Load Data
  ======================================================= */

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [
        salaryResponse,
        deductionResponse,
        employeeResponse,
      ] = await Promise.all([
        getSalaries(),
        getDeductions(),
        getEmployees(),
      ])

      setSalaries(salaryResponse)

      setDeductions(
        deductionResponse,
      )

      setEmployees(
        employeeResponse.results,
      )
    } catch (err) {
      console.error(
        "LOAD PAYROLL ERROR:",
        err,
      )

      setError(
        "خطا در دریافت اطلاعات حقوق و دستمزد.",
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  /* =======================================================
     Filtered Salaries
  ======================================================= */

  const filteredSalaries =
    useMemo(() => {
      return salaries.filter(
        (salary) => {
          if (
            salaryEmployeeFilter !==
              undefined &&
            salary.employee !==
              salaryEmployeeFilter
          ) {
            return false
          }

          if (
            salaryYear !== undefined &&
            salary.year !== salaryYear
          ) {
            return false
          }

          if (
            salaryMonth !== undefined &&
            salary.month !== salaryMonth
          ) {
            return false
          }

          return true
        },
      )
    }, [
      salaries,
      salaryEmployeeFilter,
      salaryYear,
      salaryMonth,
    ])

  /* =======================================================
     Filtered Deductions
  ======================================================= */

  const filteredDeductions =
    useMemo(() => {
      return deductions.filter(
        (deduction) => {
          if (
            deductionSalaryFilter !==
              undefined &&
            deduction.salary !==
              deductionSalaryFilter
          ) {
            return false
          }

          if (
            deductionTypeFilter &&
            deduction.deduction_type !==
              deductionTypeFilter
          ) {
            return false
          }

          return true
        },
      )
    }, [
      deductions,
      deductionSalaryFilter,
      deductionTypeFilter,
    ])

  /* =======================================================
     Options
  ======================================================= */

  const employeeOptions =
    employees.map(
      (employee) => ({
        label: `${employee.personnel_code} - ${employee.first_name} ${employee.last_name}`,
        value: employee.id,
      }),
    )

  const salaryOptions =
    salaries.map(
      (salary) => ({
        label: `${getEmployeeName(
          salary.employee,
        )} - ${getSalaryPeriod(
          salary,
        )}`,
        value: salary.id,
      }),
    )

  /* =======================================================
     Salary CRUD
  ======================================================= */

  const handleOpenCreateSalary = () => {
    setEditingSalary(null)

    salaryForm.resetFields()

    salaryForm.setFieldsValue({
      year: salaryYear ?? 1405,
      month: salaryMonth ?? 1,
      monthly_wage: 0,
      worker_food_allowance: 0,
      housing_allowance: 0,
      marriage_allowance: 0,
      notes: "",
    })

    setSalaryModalOpen(true)
  }

  const handleOpenEditSalary = (
    salary: EmployeeSalary,
  ) => {
    setEditingSalary(salary)

    salaryForm.setFieldsValue({
      employee: salary.employee,
      year: salary.year,
      month: salary.month,
      monthly_wage: Number(
        salary.monthly_wage,
      ),
      worker_food_allowance: Number(
        salary.worker_food_allowance,
      ),
      housing_allowance: Number(
        salary.housing_allowance,
      ),
      marriage_allowance: Number(
        salary.marriage_allowance,
      ),
      notes: salary.notes,
    })

    setSalaryModalOpen(true)
  }

  const handleCloseSalaryModal = () => {
    if (saving) {
      return
    }

    setSalaryModalOpen(false)
    setEditingSalary(null)
    salaryForm.resetFields()
  }

  const handleSubmitSalary = async (
    values: SalaryFormValues,
  ) => {
    try {
      setSaving(true)

      const payload = {
        employee: values.employee,
        year: values.year,
        month: values.month,
        monthly_wage: String(
          values.monthly_wage ?? 0,
        ),
        worker_food_allowance: String(
          values.worker_food_allowance ?? 0,
        ),
        housing_allowance: String(
          values.housing_allowance ?? 0,
        ),
        marriage_allowance: String(
          values.marriage_allowance ?? 0,
        ),
        notes: values.notes ?? "",
      }

      if (editingSalary) {
        await updateSalary(
          editingSalary.id,
          payload,
        )

        message.success(
          "رکورد حقوق با موفقیت ویرایش شد.",
        )
      } else {
        await createSalary(payload)

        message.success(
          "رکورد حقوق با موفقیت ایجاد شد.",
        )
      }

      setSalaryModalOpen(false)
      setEditingSalary(null)
      salaryForm.resetFields()

      await loadData()
    } catch (err) {
      console.error(
        "SAVE SALARY ERROR:",
        err,
      )

      message.error(
        "ذخیره رکورد حقوق انجام نشد.",
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteSalary = async (
    id: number,
  ) => {
    try {
      await deleteSalary(id)

      message.success(
        "رکورد حقوق با موفقیت حذف شد.",
      )

      await loadData()
    } catch (err) {
      console.error(
        "DELETE SALARY ERROR:",
        err,
      )

      message.error(
        "حذف رکورد حقوق انجام نشد.",
      )
    }
  }

  /* =======================================================
     Salary Details / Calculation
  ======================================================= */

  const handleViewSalary = (
    salary: EmployeeSalary,
  ) => {
    setSelectedSalary(salary)
    setDetailsModalOpen(true)
  }

  const handleCalculateSalary = async (
    salary: EmployeeSalary,
  ) => {
    try {
      setCalculationLoading(true)
      setCalculation(null)
      setCalculationModalOpen(true)

      const result =
        await calculateSalary(
          salary.id,
        )

      setCalculation(result)
    } catch (err) {
      console.error(
        "CALCULATE SALARY ERROR:",
        err,
      )

      message.error(
        "محاسبه حقوق انجام نشد.",
      )

      setCalculationModalOpen(false)
    } finally {
      setCalculationLoading(false)
    }
  }

  /* =======================================================
     Deduction CRUD
  ======================================================= */

  const handleOpenCreateDeduction = () => {
    setEditingDeduction(null)

    deductionForm.resetFields()

    deductionForm.setFieldsValue({
      salary:
        deductionSalaryFilter ??
        undefined,
      amount: 0,
      deduction_type: "other",
      description: "",
    })

    setDeductionModalOpen(true)
  }

  const handleOpenEditDeduction = (
    deduction: PayrollDeduction,
  ) => {
    setEditingDeduction(
      deduction,
    )

    deductionForm.setFieldsValue({
      salary: deduction.salary,
      deduction_type:
        deduction.deduction_type,
      amount: Number(
        deduction.amount,
      ),
      description:
        deduction.description,
    })

    setDeductionModalOpen(true)
  }

  const handleCloseDeductionModal =
    () => {
      if (deductionSaving) {
        return
      }

      setDeductionModalOpen(false)
      setEditingDeduction(null)
      deductionForm.resetFields()
    }

  const handleSubmitDeduction =
    async (
      values: DeductionFormValues,
    ) => {
      try {
        setDeductionSaving(true)

        const payload = {
          salary: values.salary,
          deduction_type:
            values.deduction_type,
          amount: String(
            values.amount ?? 0,
          ),
          description:
            values.description ?? "",
        }

        if (editingDeduction) {
          await updateDeduction(
            editingDeduction.id,
            payload,
          )

          message.success(
            "کسر با موفقیت ویرایش شد.",
          )
        } else {
          await createDeduction(
            payload,
          )

          message.success(
            "کسر با موفقیت ثبت شد.",
          )
        }

        setDeductionModalOpen(false)
        setEditingDeduction(null)
        deductionForm.resetFields()

        await loadData()
      } catch (err) {
        console.error(
          "SAVE DEDUCTION ERROR:",
          err,
        )

        message.error(
          "ذخیره کسر انجام نشد.",
        )
      } finally {
        setDeductionSaving(false)
      }
    }

  const handleDeleteDeduction =
    async (
      id: number,
    ) => {
      try {
        await deleteDeduction(id)

        message.success(
          "کسر با موفقیت حذف شد.",
        )

        await loadData()
      } catch (err) {
        console.error(
          "DELETE DEDUCTION ERROR:",
          err,
        )

        message.error(
          "حذف کسر انجام نشد.",
        )
      }
    }

  const handleViewDeduction = (
    deduction: PayrollDeduction,
  ) => {
    setSelectedDeduction(
      deduction,
    )

    setDeductionDetailsModalOpen(
      true,
    )
  }

  /* =======================================================
     Salary Columns
  ======================================================= */

  const salaryColumns:
    ColumnsType<EmployeeSalary> = [
      {
        title: "ردیف",
        key: "index",
        width: 70,
        align: "center",
        render: (
          _,
          __,
          index,
        ) => index + 1,
      },

      {
        title: "کارمند",
        key: "employee",
        render: (_, record) =>
          getEmployeeName(
            record.employee,
          ),
      },

      {
        title: "دوره",
        key: "period",
        align: "center",
        render: (_, record) =>
          getSalaryPeriod(record),
      },

      {
        title: "حقوق ماهانه",
        dataIndex:
          "monthly_wage",
        key: "monthly_wage",
        align: "left",
        render: (value) =>
          `${formatMoney(value)} ریال`,
      },

      {
        title: "کمک‌هزینه فرزند",
        dataIndex:
          "calculated_child_allowance",
        key:
          "calculated_child_allowance",
        align: "left",
        render: (value) =>
          `${formatMoney(value)} ریال`,
      },

      {
        title: "مزایای قابل محاسبه",
        dataIndex:
          "total_eligible_benefits",
        key:
          "total_eligible_benefits",
        align: "left",
        render: (value) =>
          `${formatMoney(value)} ریال`,
      },

      {
        title: "تعداد فرزندان مشمول",
        dataIndex:
          "eligible_children_count",
        key:
          "eligible_children_count",
        align: "center",
      },

      {
        title: "عملیات",
        key: "actions",
        fixed: "left",
        width: 190,
        render: (_, record) => (
          <Space size="small">
            <Button
              type="text"
              icon={
                <EyeOutlined />
              }
              title="مشاهده"
              onClick={() =>
                handleViewSalary(
                  record,
                )
              }
            />

            <Button
              type="text"
              icon={
                <CalculatorOutlined />
              }
              title="محاسبه"
              onClick={() =>
                handleCalculateSalary(
                  record,
                )
              }
            />

            <Button
              type="text"
              icon={
                <EditOutlined />
              }
              title="ویرایش"
              onClick={() =>
                handleOpenEditSalary(
                  record,
                )
              }
            />

            <Popconfirm
              title="حذف رکورد حقوق"
              description="آیا از حذف این رکورد اطمینان دارید؟"
              okText="بله، حذف شود"
              cancelText="انصراف"
              onConfirm={() =>
                handleDeleteSalary(
                  record.id,
                )
              }
            >
              <Button
                type="text"
                danger
                icon={
                  <DeleteOutlined />
                }
                title="حذف"
              />
            </Popconfirm>
          </Space>
        ),
      },
    ]

  /* =======================================================
     Deduction Columns
  ======================================================= */

  const deductionColumns:
    ColumnsType<PayrollDeduction> = [
      {
        title: "ردیف",
        key: "index",
        width: 70,
        align: "center",
        render: (
          _,
          __,
          index,
        ) => index + 1,
      },

      {
        title: "حقوق",
        key: "salary",
        render: (_, record) => {
          const salary =
            salaryMap.get(
              record.salary,
            )

          if (!salary) {
            return `حقوق #${record.salary}`
          }

          return `${getEmployeeName(
            salary.employee,
          )} - ${getSalaryPeriod(
            salary,
          )}`
        },
      },

      {
        title: "نوع کسر",
        dataIndex:
          "deduction_type_display",
        key:
          "deduction_type_display",
        render: (
          value,
        ) => (
          <Tag>
            {value}
          </Tag>
        ),
      },

      {
        title: "مبلغ",
        dataIndex: "amount",
        key: "amount",
        align: "left",
        render: (value) =>
          `${formatMoney(value)} ریال`,
      },

      {
        title: "توضیحات",
        dataIndex:
          "description",
        key: "description",
        render: (
          value,
        ) =>
          value || "—",
      },

      {
        title: "عملیات",
        key: "actions",
        fixed: "left",
        width: 150,
        render: (_, record) => (
          <Space size="small">
            <Button
              type="text"
              icon={
                <EyeOutlined />
              }
              title="مشاهده"
              onClick={() =>
                handleViewDeduction(
                  record,
                )
              }
            />

            <Button
              type="text"
              icon={
                <EditOutlined />
              }
              title="ویرایش"
              onClick={() =>
                handleOpenEditDeduction(
                  record,
                )
              }
            />

            <Popconfirm
              title="حذف کسر"
              description="آیا از حذف این کسر اطمینان دارید؟"
              okText="بله، حذف شود"
              cancelText="انصراف"
              onConfirm={() =>
                handleDeleteDeduction(
                  record.id,
                )
              }
            >
              <Button
                type="text"
                danger
                icon={
                  <DeleteOutlined />
                }
                title="حذف"
              />
            </Popconfirm>
          </Space>
        ),
      },
    ]

  /* =======================================================
     Selected Employee
  ======================================================= */

  const selectedEmployee =
    selectedSalary
      ? employeeMap.get(
          selectedSalary.employee,
        )
      : undefined

  /* =======================================================
     Render
  ======================================================= */

  return (
    <div
      style={{
        direction: "rtl",
      }}
    >
      <Card>
        <Space
          direction="vertical"
          size="large"
          style={{
            width: "100%",
          }}
        >
          {/* Header */}

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent:
                "space-between",
              gap: 16,
              flexWrap: "wrap",
            }}
          >
            <div>
              <Title
                level={2}
                style={{
                  margin: 0,
                }}
              >
                حقوق و دستمزد
              </Title>

              <Text type="secondary">
                مدیریت حقوق، مزایا و
                کسورات کارکنان
              </Text>
            </div>

            <Space>
              <Button
                type="primary"
                icon={
                  <PlusOutlined />
                }
                onClick={
                  handleOpenCreateSalary
                }
              >
                ثبت حقوق
              </Button>

              <Button
                icon={
                  <ReloadOutlined />
                }
                loading={loading}
                onClick={loadData}
              >
                بروزرسانی
              </Button>
            </Space>
          </div>

          {/* Error */}

          {error && (
            <Alert
              type="error"
              showIcon
              message={error}
              action={
                <Button
                  size="small"
                  onClick={loadData}
                >
                  تلاش مجدد
                </Button>
              }
            />
          )}

          {/* Loading */}

          {loading ? (
            <div
              style={{
                minHeight: 300,
                display: "flex",
                alignItems:
                  "center",
                justifyContent:
                  "center",
              }}
            >
              <Spin size="large" />
            </div>
          ) : (
            <Tabs
              defaultActiveKey="salaries"
              items={[
                /* =================================================
                   Salaries Tab
                ================================================= */

                {
                  key: "salaries",
                  label:
                    "حقوق کارکنان",

                  children: (
                    <Space
                      direction="vertical"
                      size="middle"
                      style={{
                        width: "100%",
                      }}
                    >
                      <Card
                        size="small"
                        style={{
                          background:
                            "#fafafa",
                        }}
                      >
                        <Space wrap>
                          <Select
                            allowClear
                            showSearch
                            optionFilterProp="label"
                            placeholder="کارمند"
                            prefix={
                              <SearchOutlined />
                            }
                            value={
                              salaryEmployeeFilter
                            }
                            onChange={
                              setSalaryEmployeeFilter
                            }
                            options={
                              employeeOptions
                            }
                            style={{
                              width: 280,
                            }}
                          />

                          <InputNumber
                            placeholder="سال"
                            min={1300}
                            max={1500}
                            value={
                              salaryYear
                            }
                            onChange={(
                              value,
                            ) =>
                              setSalaryYear(
                                value ??
                                  undefined,
                              )
                            }
                            style={{
                              width: 140,
                            }}
                          />

                          <Select
                            allowClear
                            placeholder="ماه"
                            value={
                              salaryMonth
                            }
                            onChange={
                              setSalaryMonth
                            }
                            options={
                              monthOptions
                            }
                            style={{
                              width: 150,
                            }}
                          />

                          <Button
                            onClick={() => {
                              setSalaryEmployeeFilter(
                                undefined,
                              )

                              setSalaryYear(
                                undefined,
                              )

                              setSalaryMonth(
                                undefined,
                              )
                            }}
                          >
                            پاک کردن فیلترها
                          </Button>
                        </Space>
                      </Card>

                      <Table<EmployeeSalary>
                        rowKey="id"
                        columns={
                          salaryColumns
                        }
                        dataSource={
                          filteredSalaries
                        }
                        pagination={{
                          pageSize: 10,
                          showSizeChanger:
                            true,
                          showTotal:
                            (
                              total,
                            ) =>
                              `تعداد ${total} حقوق`,
                        }}
                        scroll={{
                          x: 1300,
                        }}
                        locale={{
                          emptyText:
                            "هیچ رکورد حقوقی یافت نشد",
                        }}
                      />
                    </Space>
                  ),
                },

                /* =================================================
                   Deductions Tab
                ================================================= */

                {
                  key: "deductions",
                  label:
                    "کسورات",

                  children: (
                    <Space
                      direction="vertical"
                      size="middle"
                      style={{
                        width: "100%",
                      }}
                    >
                      <Card
                        size="small"
                        style={{
                          background:
                            "#fafafa",
                        }}
                      >
                        <Space
                          wrap
                          style={{
                            width: "100%",
                            justifyContent:
                              "space-between",
                          }}
                        >
                          <Space wrap>
                            <Select
                              allowClear
                              showSearch
                              optionFilterProp="label"
                              placeholder="حقوق"
                              value={
                                deductionSalaryFilter
                              }
                              onChange={
                                setDeductionSalaryFilter
                              }
                              options={
                                salaryOptions
                              }
                              style={{
                                width: 300,
                              }}
                            />

                            <Select
                              allowClear
                              placeholder="نوع کسر"
                              value={
                                deductionTypeFilter
                              }
                              onChange={
                                setDeductionTypeFilter
                              }
                              options={
                                deductionTypeOptions
                              }
                              style={{
                                width: 180,
                              }}
                            />

                            <Button
                              onClick={() => {
                                setDeductionSalaryFilter(
                                  undefined,
                                )

                                setDeductionTypeFilter(
                                  undefined,
                                )
                              }}
                            >
                              پاک کردن فیلترها
                            </Button>
                          </Space>

                          <Button
                            type="primary"
                            icon={
                              <PlusOutlined />
                            }
                            onClick={
                              handleOpenCreateDeduction
                            }
                          >
                            ثبت کسر
                          </Button>
                        </Space>
                      </Card>

                      <Table<PayrollDeduction>
                        rowKey="id"
                        columns={
                          deductionColumns
                        }
                        dataSource={
                          filteredDeductions
                        }
                        pagination={{
                          pageSize: 10,
                          showSizeChanger:
                            true,
                          showTotal:
                            (
                              total,
                            ) =>
                              `تعداد ${total} کسر`,
                        }}
                        scroll={{
                          x: 1050,
                        }}
                        locale={{
                          emptyText:
                            "هیچ کسوری یافت نشد",
                        }}
                      />
                    </Space>
                  ),
                },
              ]}
            />
          )}
        </Space>
      </Card>

      {/* =====================================================
          Salary Modal
      ===================================================== */}

      <Modal
        title={
          editingSalary
            ? "ویرایش رکورد حقوق"
            : "ثبت حقوق جدید"
        }
        open={salaryModalOpen}
        onCancel={
          handleCloseSalaryModal
        }
        footer={null}
        destroyOnHidden
        width={650}
      >
        <Form
          form={salaryForm}
          layout="vertical"
          onFinish={
            handleSubmitSalary
          }
          style={{
            marginTop: 20,
          }}
        >
          <Form.Item
            label="کارمند"
            name="employee"
            rules={[
              {
                required: true,
                message:
                  "انتخاب کارمند الزامی است.",
              },
            ]}
          >
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="کارمند را انتخاب کنید"
              options={
                employeeOptions
              }
            />
          </Form.Item>

          <Space
            style={{
              width: "100%",
            }}
            size="middle"
          >
            <Form.Item
              label="سال"
              name="year"
              rules={[
                {
                  required: true,
                  message:
                    "سال الزامی است.",
                },
              ]}
            >
              <InputNumber
                min={1300}
                max={1500}
                style={{
                  width: 180,
                }}
              />
            </Form.Item>

            <Form.Item
              label="ماه"
              name="month"
              rules={[
                {
                  required: true,
                  message:
                    "ماه الزامی است.",
                },
              ]}
            >
              <Select
                options={
                  monthOptions
                }
                style={{
                  width: 180,
                }}
              />
            </Form.Item>
          </Space>

          <Form.Item
            label="مزد ماهیانه"
            name="monthly_wage"
            rules={[
              {
                required: true,
                message:
                  "مزد ماهیانه الزامی است.",
              },
              {
                type: "number",
                min: 0,
                message:
                  "مبلغ نمی‌تواند منفی باشد.",
              },
            ]}
          >
            <InputNumber
              min={0}
              controls
              style={{
                width: "100%",
              }}
              addonAfter="ریال"
            />
          </Form.Item>

          <Space
            style={{
              width: "100%",
            }}
            size="middle"
          >
            <Form.Item
              label="بن کارگری"
              name="worker_food_allowance"
            >
              <InputNumber
                min={0}
                style={{
                  width: 250,
                }}
                addonAfter="ریال"
              />
            </Form.Item>

            <Form.Item
              label="حق مسکن"
              name="housing_allowance"
            >
              <InputNumber
                min={0}
                style={{
                  width: 250,
                }}
                addonAfter="ریال"
              />
            </Form.Item>
          </Space>

          <Form.Item
            label="حق تأهل"
            name="marriage_allowance"
          >
            <InputNumber
              min={0}
              style={{
                width: "100%",
              }}
              addonAfter="ریال"
            />
          </Form.Item>

          <Form.Item
            label="توضیحات"
            name="notes"
          >
            <Input.TextArea
              rows={4}
              placeholder="توضیحات اختیاری"
            />
          </Form.Item>

          <Divider />

          <Space
            style={{
              width: "100%",
              justifyContent:
                "flex-start",
            }}
          >
            <Button
              type="primary"
              htmlType="submit"
              loading={saving}
            >
              {editingSalary
                ? "ذخیره تغییرات"
                : "ثبت حقوق"}
            </Button>

            <Button
              onClick={
                handleCloseSalaryModal
              }
              disabled={saving}
            >
              انصراف
            </Button>
          </Space>
        </Form>
      </Modal>

      {/* =====================================================
          Salary Details Modal
      ===================================================== */}

      <Modal
        title="جزئیات رکورد حقوق"
        open={detailsModalOpen}
        onCancel={() =>
          setDetailsModalOpen(false)
        }
        footer={null}
        width={750}
      >
        {selectedSalary && (
          <Descriptions
            bordered
            column={2}
            size="middle"
            style={{
              marginTop: 20,
            }}
          >
            <Descriptions.Item label="کارمند">
              {selectedEmployee
                ? `${selectedEmployee.personnel_code} - ${selectedEmployee.first_name} ${selectedEmployee.last_name}`
                : `کارمند #${selectedSalary.employee}`}
            </Descriptions.Item>

            <Descriptions.Item label="دوره">
              {getSalaryPeriod(
                selectedSalary,
              )}
            </Descriptions.Item>

            <Descriptions.Item label="حقوق ماهانه">
              {formatMoney(
                selectedSalary.monthly_wage,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="بن کارگری">
              {formatMoney(
                selectedSalary.worker_food_allowance,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="حق مسکن">
              {formatMoney(
                selectedSalary.housing_allowance,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="حق تأهل">
              {formatMoney(
                selectedSalary.marriage_allowance,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="تعداد فرزندان مشمول">
              {
                selectedSalary.eligible_children_count
              }
            </Descriptions.Item>

            <Descriptions.Item label="حق اولاد محاسبه‌شده">
              {formatMoney(
                selectedSalary.calculated_child_allowance,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="مزد روزانه">
              {formatMoney(
                selectedSalary.daily_wage,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="مزایای قابل محاسبه">
              {formatMoney(
                selectedSalary.total_eligible_benefits,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item
              label="توضیحات"
              span={2}
            >
              {selectedSalary.notes ||
                "—"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>

      {/* =====================================================
          Salary Calculation Modal
      ===================================================== */}

      <Modal
        title="محاسبه کامل حقوق"
        open={calculationModalOpen}
        onCancel={() =>
          setCalculationModalOpen(false)
        }
        footer={null}
        width={800}
      >
        {calculationLoading ? (
          <div
            style={{
              minHeight: 300,
              display: "flex",
              alignItems:
                "center",
              justifyContent:
                "center",
            }}
          >
            <Spin size="large" />
          </div>
        ) : calculation ? (
          <Space
            direction="vertical"
            size="large"
            style={{
              width: "100%",
              marginTop: 16,
            }}
          >
            <Descriptions
              bordered
              column={2}
            >
              <Descriptions.Item label="کارمند">
                {getEmployeeName(
                  calculation.employee,
                )}
              </Descriptions.Item>

              <Descriptions.Item label="دوره">
                {calculation.period.year}/
                {String(
                  calculation.period.month,
                ).padStart(2, "0")}
              </Descriptions.Item>
            </Descriptions>

            <Card
              title="درآمدها و مزایا"
              size="small"
            >
              <Descriptions
                column={2}
                bordered
              >
                <Descriptions.Item label="حقوق ماهانه">
                  {formatMoney(
                    calculation
                      .earnings
                      .monthly_wage,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="بن کارگری">
                  {formatMoney(
                    calculation
                      .earnings
                      .worker_food_allowance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="حق مسکن">
                  {formatMoney(
                    calculation
                      .earnings
                      .housing_allowance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="حق تأهل">
                  {formatMoney(
                    calculation
                      .earnings
                      .marriage_allowance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="حق اولاد">
                  {formatMoney(
                    calculation
                      .earnings
                      .child_allowance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="ناخالص دریافتی">
                  <Text strong>
                    {formatMoney(
                      calculation
                        .earnings
                        .gross_earnings,
                    )}{" "}
                    ریال
                  </Text>
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Card
              title="فرزندان"
              size="small"
            >
              <Descriptions
                column={2}
                bordered
              >
                <Descriptions.Item label="تعداد مشمول">
                  {
                    calculation
                      .children
                      .eligible_count
                  }
                </Descriptions.Item>

                <Descriptions.Item label="حق اولاد هر فرزند">
                  {formatMoney(
                    calculation
                      .children
                      .allowance_per_child,
                  )}{" "}
                  ریال
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Card
              title="کسورات"
              size="small"
            >
              <Descriptions
                column={2}
                bordered
              >
                <Descriptions.Item label="بیمه">
                  {formatMoney(
                    calculation
                      .deductions
                      .insurance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="مالیات">
                  {formatMoney(
                    calculation
                      .deductions
                      .tax,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="مساعده">
                  {formatMoney(
                    calculation
                      .deductions
                      .advance,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="وام">
                  {formatMoney(
                    calculation
                      .deductions
                      .loan,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="غیبت / کسرکار">
                  {formatMoney(
                    calculation
                      .deductions
                      .absence,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="سایر">
                  {formatMoney(
                    calculation
                      .deductions
                      .other,
                  )}{" "}
                  ریال
                </Descriptions.Item>

                <Descriptions.Item label="مجموع کسورات">
                  <Text strong>
                    {formatMoney(
                      calculation
                        .deductions
                        .total_deductions,
                    )}{" "}
                    ریال
                  </Text>
                </Descriptions.Item>
              </Descriptions>
            </Card>

            <Card
              size="small"
              style={{
                textAlign: "center",
              }}
            >
              <Text strong>
                حقوق خالص
              </Text>

              <div
                style={{
                  fontSize: 28,
                  fontWeight: 700,
                  marginTop: 8,
                }}
              >
                {formatMoney(
                  calculation.net_salary,
                )}{" "}
                ریال
              </div>
            </Card>
          </Space>
        ) : (
          <Alert
            type="warning"
            message="اطلاعات محاسبه در دسترس نیست."
          />
        )}
      </Modal>

      {/* =====================================================
          Deduction Modal
      ===================================================== */}

      <Modal
        title={
          editingDeduction
            ? "ویرایش کسر"
            : "ثبت کسر جدید"
        }
        open={deductionModalOpen}
        onCancel={
          handleCloseDeductionModal
        }
        footer={null}
        destroyOnHidden
        width={600}
      >
        <Form
          form={deductionForm}
          layout="vertical"
          onFinish={
            handleSubmitDeduction
          }
          style={{
            marginTop: 20,
          }}
        >
          <Form.Item
            label="حقوق"
            name="salary"
            rules={[
              {
                required: true,
                message:
                  "انتخاب حقوق الزامی است.",
              },
            ]}
          >
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="حقوق را انتخاب کنید"
              options={
                salaryOptions
              }
            />
          </Form.Item>

          <Form.Item
            label="نوع کسر"
            name="deduction_type"
            rules={[
              {
                required: true,
                message:
                  "نوع کسر را انتخاب کنید.",
              },
            ]}
          >
            <Select
              placeholder="نوع کسر"
              options={
                deductionTypeOptions
              }
            />
          </Form.Item>

          <Form.Item
            label="مبلغ"
            name="amount"
            rules={[
              {
                required: true,
                message:
                  "مبلغ کسر الزامی است.",
              },
              {
                type: "number",
                min: 0,
                message:
                  "مبلغ نمی‌تواند منفی باشد.",
              },
            ]}
          >
            <InputNumber
              min={0}
              controls
              style={{
                width: "100%",
              }}
              addonAfter="ریال"
            />
          </Form.Item>

          <Form.Item
            label="توضیحات"
            name="description"
          >
            <Input.TextArea
              rows={4}
              placeholder="توضیحات اختیاری"
            />
          </Form.Item>

          <Divider />

          <Space>
            <Button
              type="primary"
              htmlType="submit"
              loading={
                deductionSaving
              }
            >
              {editingDeduction
                ? "ذخیره تغییرات"
                : "ثبت کسر"}
            </Button>

            <Button
              onClick={
                handleCloseDeductionModal
              }
              disabled={
                deductionSaving
              }
            >
              انصراف
            </Button>
          </Space>
        </Form>
      </Modal>

      {/* =====================================================
          Deduction Details Modal
      ===================================================== */}

      <Modal
        title="جزئیات کسر"
        open={
          deductionDetailsModalOpen
        }
        onCancel={() =>
          setDeductionDetailsModalOpen(
            false,
          )
        }
        footer={null}
        width={650}
      >
        {selectedDeduction && (
          <Descriptions
            bordered
            column={2}
            size="middle"
            style={{
              marginTop: 20,
            }}
          >
            <Descriptions.Item label="حقوق">
              {(() => {
                const salary =
                  salaryMap.get(
                    selectedDeduction.salary,
                  )

                if (!salary) {
                  return `حقوق #${selectedDeduction.salary}`
                }

                return `${getEmployeeName(
                  salary.employee,
                )} - ${getSalaryPeriod(
                  salary,
                )}`
              })()}
            </Descriptions.Item>

            <Descriptions.Item label="نوع کسر">
              <Tag>
                {
                  selectedDeduction.deduction_type_display
                }
              </Tag>
            </Descriptions.Item>

            <Descriptions.Item label="مبلغ">
              {formatMoney(
                selectedDeduction.amount,
              )}{" "}
              ریال
            </Descriptions.Item>

            <Descriptions.Item label="شناسه">
              {selectedDeduction.id}
            </Descriptions.Item>

            <Descriptions.Item
              label="توضیحات"
              span={2}
            >
              {selectedDeduction.description ||
                "—"}
            </Descriptions.Item>

            <Descriptions.Item label="تاریخ ایجاد">
              {selectedDeduction.created_at
                ? new Date(
                    selectedDeduction.created_at,
                  ).toLocaleString(
                    "fa-IR",
                  )
                : "—"}
            </Descriptions.Item>

            <Descriptions.Item label="آخرین بروزرسانی">
              {selectedDeduction.updated_at
                ? new Date(
                    selectedDeduction.updated_at,
                  ).toLocaleString(
                    "fa-IR",
                  )
                : "—"}
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  )
}