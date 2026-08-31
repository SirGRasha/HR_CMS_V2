import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Input,
  InputNumber,
  Modal,
  Row,
  Select,
  Space,
  Spin,
  Table,
  Tag,
  Typography,
  message,
} from "antd"
import type { ColumnsType } from "antd/es/table"
import {
  PlusOutlined,
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  EditOutlined,
  StopOutlined,
  CheckCircleOutlined,
} from "@ant-design/icons"
import { useEffect, useMemo, useState } from "react"

import {
  createEmployee,
  getEmployee,
  getEmployees,
  patchEmployee,
} from "../../api/employees"

import {
  getOrganizationUnits,
  getPositions,
} from "../../api/organization"

import type {
  Employee,
} from "../../types/employee"

import type {
  OrganizationUnit,
  Position,
} from "../../types/organization"

const { Title, Text } = Typography

interface EmployeeFormValues {
  personnel_code: string
  first_name: string
  last_name: string
  national_id: string
  birth_certificate_number?: string
  father_name?: string

  gender: string
  employee_group: string
  marital_status: string
  military_status?: string

  department?: string
  job_title?: string
  position?: number

  education_level?: string
  field_of_study?: string
  student_number?: string

  child_count?: number

  landline_phone?: string
  residence_area?: string
  address?: string

  transportation_status?: string
  transportation_description?: string

  contract_title?: string
  contract_position?: string

  insurance_number?: string

  birth_date?: string
  start_date?: string
  insurance_date?: string

  notes?: string
}

const genderOptions = [
  {
    label: "مرد",
    value: "male",
  },
  {
    label: "زن",
    value: "female",
  },
]

const employeeGroupOptions = [
  {
    label: "اداری",
    value: "administrative",
  },
  {
    label: "تولید",
    value: "production",
  },
]

const maritalStatusOptions = [
  {
    label: "مجرد",
    value: "single",
  },
  {
    label: "متأهل",
    value: "married",
  },
  {
    label: "متارکه",
    value: "separated",
  },
  {
    label: "بیوه",
    value: "widowed",
  },
]

const militaryStatusOptions = [
  {
    label: "مشمول",
    value: "subject",
  },
  {
    label: "معافیت",
    value: "exemption",
  },
  {
    label: "پایان خدمت",
    value: "completed",
  },
  {
    label: "در حال خدمت",
    value: "serving",
  },
  {
    label: "معافیت تحصیلی",
    value: "educational_exemption",
  },
]

const transportationStatusOptions = [
  {
    label: "شخصی",
    value: "personal",
  },
  {
    label: "سرویس",
    value: "service",
  },
]

function getEmployeeGroupLabel(value: string) {
  return (
    employeeGroupOptions.find(
      (item) => item.value === value,
    )?.label ?? value
  )
}

function getGenderLabel(value: string) {
  const labels: Record<string, string> = {
    male: "مرد",
    female: "زن",
  }

  return labels[value] ?? value
}

function getMaritalStatusLabel(value: string) {
  const labels: Record<string, string> = {
    single: "مجرد",
    married: "متأهل",
    separated: "متارکه",
    widowed: "بیوه",
  }

  return labels[value] ?? value
}

function getMilitaryStatusLabel(value: string) {
  const labels: Record<string, string> = {
    subject: "مشمول",
    exemption: "معافیت",
    completed: "پایان خدمت",
    serving: "در حال خدمت",
    educational_exemption: "معافیت تحصیلی",
  }

  return labels[value] ?? value
}

function getTransportationStatusLabel(value: string) {
  const labels: Record<string, string> = {
    personal: "شخصی",
    service: "سرویس",
  }

  return labels[value] ?? value
}

function displayValue(value: unknown): string {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—"
  }

  return String(value)
}

function formatJalaliDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return "—"
  }

  return value
}

function getApiErrorMessage(err: unknown): string {
  if (
    err &&
    typeof err === "object"
  ) {
    const error = err as {
      status?: number
      data?: unknown
      message?: string
    }

    if (
      error.data &&
      typeof error.data === "object"
    ) {
      const data = err as {
        data?: Record<string, unknown>
      }

      if (data.data) {
        const messages: string[] = []

        Object.entries(data.data).forEach(
          ([field, value]) => {
            if (Array.isArray(value)) {
              value.forEach((item) => {
                messages.push(
                  `${field}: ${String(item)}`,
                )
              })
            } else if (
              value !== undefined &&
              value !== null
            ) {
              messages.push(
                `${field}: ${String(value)}`,
              )
            }
          },
        )

        if (messages.length > 0) {
          return messages.join(" | ")
        }
      }
    }

    if (error.message) {
      return error.message
    }

    if (error.status) {
      return `خطای سرور (${error.status})`
    }
  }

  return "خطایی در ارتباط با سرور رخ داد."
}

export default function EmployeesPage() {
  const [form] =
    Form.useForm<EmployeeFormValues>()

  const [employees, setEmployees] =
    useState<Employee[]>([])

  const [loading, setLoading] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [statusChangingId, setStatusChangingId] =
    useState<number | null>(null)

  const [error, setError] =
    useState<string | null>(null)

  const [search, setSearch] =
    useState("")

  const [activeFilter, setActiveFilter] =
    useState<boolean | undefined>(
      undefined,
    )

  const [modalOpen, setModalOpen] =
    useState(false)

  const [viewModalOpen, setViewModalOpen] =
    useState(false)

  const [selectedEmployee, setSelectedEmployee] =
    useState<Employee | null>(null)

  const [editingEmployee, setEditingEmployee] =
    useState<Employee | null>(null)

  const [viewLoading, setViewLoading] =
    useState(false)

  const [organizationUnits, setOrganizationUnits] =
    useState<OrganizationUnit[]>([])

  const [positions, setPositions] =
    useState<Position[]>([])

  const [organizationLoading, setOrganizationLoading] =
    useState(false)

  const [positionLoading, setPositionLoading] =
    useState(false)

  const [selectedOrganizationUnitId, setSelectedOrganizationUnitId] =
    useState<number | undefined>(undefined)

  const loadEmployees = async () => {
    try {
      setLoading(true)
      setError(null)

      const response =
        await getEmployees({
          is_active: activeFilter,
        })

      setEmployees(
        response.results,
      )
    } catch (err) {
      console.error(
        "LOAD EMPLOYEES ERROR:",
        err,
      )

      const errorMessage =
        getApiErrorMessage(err)

      setError(
        `خطا در دریافت فهرست کارکنان: ${errorMessage}`,
      )
    } finally {
      setLoading(false)
    }
  }

  const loadOrganizationUnits = async () => {
    try {
      setOrganizationLoading(true)

      const response =
        await getOrganizationUnits({
          is_active: true,
        })

      setOrganizationUnits(response)
    } catch (err) {
      console.error(
        "LOAD ORGANIZATION UNITS ERROR:",
        err,
      )

      message.error(
        `خطا در دریافت واحدهای سازمانی: ${getApiErrorMessage(err)}`,
      )
    } finally {
      setOrganizationLoading(false)
    }
  }

  const loadPositions = async (
    organizationUnitId?: number,
  ) => {
    try {
      setPositionLoading(true)

      if (
        organizationUnitId === undefined
      ) {
        setPositions([])
        return
      }

      const response =
        await getPositions({
          is_active: true,
          organization_unit:
            organizationUnitId,
        })

      setPositions(response)
    } catch (err) {
      console.error(
        "LOAD POSITIONS ERROR:",
        err,
      )

      message.error(
        `خطا در دریافت سمت‌های سازمانی: ${getApiErrorMessage(err)}`,
      )

      setPositions([])
    } finally {
      setPositionLoading(false)
    }
  }

  useEffect(() => {
    loadEmployees()
  }, [activeFilter])

  useEffect(() => {
    loadOrganizationUnits()
  }, [])

  const filteredEmployees =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase()

      if (!query) {
        return employees
      }

      return employees.filter(
        (employee) =>
          [
            employee.personnel_code,
            employee.first_name,
            employee.last_name,
            employee.national_id,
            employee.job_title,
            employee.department,
          ]
            .filter(Boolean)
            .some((value) =>
              String(value)
                .toLowerCase()
                .includes(query),
            ),
      )
    }, [employees, search])

  const handleViewEmployee = async (
    employeeId: number,
  ) => {
    try {
      setViewLoading(true)
      setSelectedEmployee(null)
      setViewModalOpen(true)

      const employee =
        await getEmployee(employeeId)

      setSelectedEmployee(employee)
    } catch (err) {
      console.error(
        "GET EMPLOYEE ERROR:",
        err,
      )

      message.error(
        getApiErrorMessage(err),
      )

      setViewModalOpen(false)
    } finally {
      setViewLoading(false)
    }
  }

  const handleEditEmployee = async (
    employeeId: number,
  ) => {
    try {
      setSaving(true)

      const employee =
        await getEmployee(employeeId)

      setEditingEmployee(employee)

      const organizationUnitId =
        employee.position_detail
          ?.organization_unit
          ?.id

      setSelectedOrganizationUnitId(
        organizationUnitId,
      )

      if (
        organizationUnitId !== undefined
      ) {
        await loadPositions(
          organizationUnitId,
        )
      } else {
        setPositions([])
      }

      form.setFieldsValue({
        personnel_code:
          employee.personnel_code,

        first_name:
          employee.first_name,

        last_name:
          employee.last_name,

        national_id:
          employee.national_id,

        birth_certificate_number:
          employee.birth_certificate_number ??
          "",

        father_name:
          employee.father_name ?? "",

        gender:
          employee.gender,

        employee_group:
          employee.employee_group,

        marital_status:
          employee.marital_status,

        military_status:
          employee.military_status ?? "",

        department:
          employee.department ?? "",

        job_title:
          employee.job_title ?? "",

        position:
          employee.position ?? undefined,

        education_level:
          employee.education_level ?? "",

        field_of_study:
          employee.field_of_study ?? "",

        student_number:
          employee.student_number ?? "",

        child_count:
          employee.child_count ?? 0,

        landline_phone:
          employee.landline_phone ?? "",

        residence_area:
          employee.residence_area ?? "",

        address:
          employee.address ?? "",

        transportation_status:
          employee.transportation_status ?? "",

        transportation_description:
          employee.transportation_description ??
          "",

        contract_title:
          employee.contract_title ?? "",

        contract_position:
          employee.contract_position ?? "",

        insurance_number:
          employee.insurance_number ?? "",

        birth_date:
          employee.birth_date ?? undefined,

        start_date:
          employee.start_date ?? undefined,

        insurance_date:
          employee.insurance_date ?? undefined,

        notes:
          employee.notes ?? "",
      })

      setModalOpen(true)
    } catch (err) {
      console.error(
        "GET EMPLOYEE FOR EDIT ERROR:",
        err,
      )

      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const handleOpenCreate = () => {
    setEditingEmployee(null)

    setSelectedOrganizationUnitId(
      undefined,
    )

    setPositions([])

    form.resetFields()

    form.setFieldsValue({
      child_count: 0,
      gender: "male",
      employee_group: "administrative",
      marital_status: "single",
    })

    setModalOpen(true)
  }

  const handleOrganizationUnitChange = async (
    value: number | undefined,
  ) => {
    setSelectedOrganizationUnitId(
      value,
    )

    form.setFieldValue(
      "position",
      undefined,
    )

    setPositions([])

    if (value !== undefined) {
      await loadPositions(value)
    }
  }

  const handleCloseCreate = () => {
    if (saving) {
      return
    }

    setModalOpen(false)
    setEditingEmployee(null)
    setSelectedOrganizationUnitId(
      undefined,
    )
    setPositions([])
    form.resetFields()
  }

  const handleCreate = async () => {
    try {
      const values =
        await form.validateFields()

      setSaving(true)

      const payload = {
        personnel_code:
          values.personnel_code,

        first_name:
          values.first_name,

        last_name:
          values.last_name,

        national_id:
          values.national_id,

        birth_certificate_number:
          values.birth_certificate_number ?? "",

        father_name:
          values.father_name ?? "",

        gender:
          values.gender,

        employee_group:
          values.employee_group,

        marital_status:
          values.marital_status,

        military_status:
          values.military_status ?? "",

        department:
          values.department ?? "",

        job_title:
          values.job_title ?? "",

        position:
          values.position ?? null,

        education_level:
          values.education_level ?? "",

        field_of_study:
          values.field_of_study ?? "",

        student_number:
          values.student_number ?? "",

        child_count:
          values.child_count ?? 0,

        landline_phone:
          values.landline_phone ?? "",

        residence_area:
          values.residence_area ?? "",

        address:
          values.address ?? "",

        transportation_status:
          values.transportation_status ?? "",

        transportation_description:
          values.transportation_description ?? "",

        contract_title:
          values.contract_title ?? "",

        contract_position:
          values.contract_position ?? "",

        insurance_number:
          values.insurance_number ?? "",

        birth_date:
          values.birth_date || null,

        start_date:
          values.start_date || null,

        insurance_date:
          values.insurance_date || null,

        notes:
          values.notes ?? "",
      }

      if (editingEmployee) {
        await patchEmployee(
          editingEmployee.id,
          payload,
        )

        message.success(
          "اطلاعات کارمند با موفقیت ویرایش شد.",
        )
      } else {
        await createEmployee({
          ...payload,
          is_active: true,
        })

        message.success(
          "کارمند با موفقیت ثبت شد.",
        )
      }

      setModalOpen(false)
      setEditingEmployee(null)
      setSelectedOrganizationUnitId(
        undefined,
      )
      setPositions([])
      form.resetFields()

      await loadEmployees()
    } catch (err) {
      console.error(
        "SAVE EMPLOYEE ERROR:",
        err,
      )

      if (
        err &&
        typeof err === "object" &&
        "errorFields" in err
      ) {
        return
      }

      const errorMessage =
        getApiErrorMessage(err)

      message.error(
        `${editingEmployee ? "ویرایش" : "ثبت"} کارمند با خطا مواجه شد: ${errorMessage}`,
        6,
      )
    } finally {
      setSaving(false)
    }
  }

  const handleToggleEmployeeStatus = (
    employee: Employee,
  ) => {
    const nextStatus =
      !employee.is_active

    const actionText =
      nextStatus
        ? "فعال کردن"
        : "غیرفعال کردن"

    const successText =
      nextStatus
        ? "کارمند با موفقیت فعال شد."
        : "کارمند با موفقیت غیرفعال شد."

    Modal.confirm({
      title: `${actionText} کارمند`,
      content: (
        <div dir="rtl">
          آیا از {actionText} کارمند{" "}
          <strong>
            {employee.first_name}{" "}
            {employee.last_name}
          </strong>{" "}
          با کد پرسنلی{" "}
          <strong>
            {employee.personnel_code}
          </strong>{" "}
          اطمینان دارید؟
        </div>
      ),
      okText: actionText,
      cancelText: "انصراف",
      centered: true,
      okButtonProps: {
        danger: !nextStatus,
      },
      onOk: async () => {
        try {
          setStatusChangingId(
            employee.id,
          )

          await patchEmployee(
            employee.id,
            {
              is_active: nextStatus,
            },
          )

          message.success(
            successText,
          )

          await loadEmployees()

          if (
            selectedEmployee?.id ===
            employee.id
          ) {
            setSelectedEmployee({
              ...selectedEmployee,
              is_active: nextStatus,
            })
          }
        } catch (err) {
          console.error(
            "TOGGLE EMPLOYEE STATUS ERROR:",
            err,
          )

          message.error(
            `${actionText} کارمند با خطا مواجه شد: ${getApiErrorMessage(err)}`,
            6,
          )

          throw err
        } finally {
          setStatusChangingId(null)
        }
      },
    })
  }

  const columns: ColumnsType<Employee> =
    [
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
        title: "کد پرسنلی",
        dataIndex:
          "personnel_code",
        key: "personnel_code",
      },

      {
        title:
          "نام و نام خانوادگی",
        key: "full_name",
        render: (
          _,
          record,
        ) =>
          `${record.first_name} ${record.last_name}`,
      },

      {
        title:
          "کد ملی",
        dataIndex:
          "national_id",
        key: "national_id",
      },

      {
        title:
          "سمت",
        key: "position",
        render: (
          _,
          record,
        ) =>
          record.position_detail
            ?.title ??
          record.job_title ??
          "—",
      },

      {
        title:
          "واحد سازمانی",
        key: "organization_unit",
        render: (
          _,
          record,
        ) =>
          record.position_detail
            ?.organization_unit
            ?.name ??
          record.department ??
          "—",
      },

      {
        title:
          "گروه پرسنلی",
        dataIndex:
          "employee_group",
        key: "employee_group",
        render: (
          value: string,
        ) =>
          getEmployeeGroupLabel(
            value,
          ),
      },

      {
        title: "وضعیت",
        dataIndex:
          "is_active",
        key: "is_active",
        align: "center",
        render: (
          isActive: boolean,
        ) =>
          isActive ? (
            <Tag color="success">
              فعال
            </Tag>
          ) : (
            <Tag color="error">
              غیرفعال
            </Tag>
          ),
      },

      {
        title:
          "عملیات",
        key: "actions",
        align: "center",
        width: 330,
        render: (_, record) => (
          <Space>
            <Button
              type="link"
              icon={
                <EyeOutlined />
              }
              onClick={() =>
                handleViewEmployee(
                  record.id,
                )
              }
            >
              مشاهده
            </Button>

            <Button
              type="link"
              icon={
                <EditOutlined />
              }
              onClick={() =>
                handleEditEmployee(
                  record.id,
                )
              }
            >
              ویرایش
            </Button>

            {record.is_active ? (
              <Button
                type="link"
                danger
                icon={
                  <StopOutlined />
                }
                loading={
                  statusChangingId ===
                  record.id
                }
                onClick={() =>
                  handleToggleEmployeeStatus(
                    record,
                  )
                }
              >
                غیرفعال کردن
              </Button>
            ) : (
              <Button
                type="link"
                icon={
                  <CheckCircleOutlined />
                }
                loading={
                  statusChangingId ===
                  record.id
                }
                onClick={() =>
                  handleToggleEmployeeStatus(
                    record,
                  )
                }
              >
                فعال کردن
              </Button>
            )}
          </Space>
        ),
      },
    ]

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
              alignItems:
                "center",
              justifyContent:
                "space-between",
              gap: 16,
              flexWrap:
                "wrap",
            }}
          >
            <div>
              <Title
                level={2}
                style={{
                  margin: 0,
                }}
              >
                کارکنان
              </Title>

              <Text type="secondary">
                مدیریت اطلاعات کارکنان
              </Text>
            </div>

            <Space>
              <Button
                icon={
                  <ReloadOutlined />
                }
                onClick={
                  loadEmployees
                }
                loading={loading}
              >
                بروزرسانی
              </Button>

              <Button
                type="primary"
                icon={
                  <PlusOutlined />
                }
                onClick={
                  handleOpenCreate
                }
              >
                افزودن کارمند
              </Button>
            </Space>
          </div>

          {/* Filters */}
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
              }}
            >
              <Input
                allowClear
                prefix={
                  <SearchOutlined />
                }
                placeholder="جستجو در کارکنان..."
                value={search}
                onChange={(event) =>
                  setSearch(
                    event.target.value,
                  )
                }
                style={{
                  width: 300,
                }}
              />

              <Select
                allowClear
                placeholder="وضعیت"
                style={{
                  width: 160,
                }}
                value={
                  activeFilter
                }
                onChange={(
                  value,
                ) =>
                  setActiveFilter(
                    value,
                  )
                }
                options={[
                  {
                    label: "همه",
                    value:
                      undefined,
                  },
                  {
                    label: "فعال",
                    value: true,
                  },
                  {
                    label:
                      "غیرفعال",
                    value: false,
                  },
                ]}
              />
            </Space>
          </Card>

          {/* Error */}
          {error && (
            <Alert
              type="error"
              showIcon
              message={error}
              action={
                <Button
                  size="small"
                  onClick={
                    loadEmployees
                  }
                >
                  تلاش مجدد
                </Button>
              }
            />
          )}

          {/* Table */}
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
            <Table<Employee>
              rowKey="id"
              columns={columns}
              dataSource={
                filteredEmployees
              }
              scroll={{
                x: 1500,
              }}
              pagination={{
                pageSize: 10,
                showSizeChanger:
                  true,
                showTotal: (
                  total,
                ) =>
                  `تعداد ${total} کارمند`,
              }}
              locale={{
                emptyText:
                  "هیچ کارمندی یافت نشد",
              }}
            />
          )}
        </Space>
      </Card>

      {/* Employee Details Modal */}
      <Modal
        title="مشاهده اطلاعات کارمند"
        open={viewModalOpen}
        onCancel={() => {
          if (viewLoading) {
            return
          }

          setViewModalOpen(false)
          setSelectedEmployee(null)
        }}
        width={900}
        centered
        footer={[
          <Button
            key="close"
            onClick={() => {
              setViewModalOpen(false)
              setSelectedEmployee(null)
            }}
            disabled={viewLoading}
          >
            بستن
          </Button>,
        ]}
      >
        {viewLoading ? (
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
        ) : selectedEmployee ? (
          <Space
            direction="vertical"
            size="large"
            style={{
              width: "100%",
              marginTop: 20,
            }}
          >
            {/* اطلاعات اصلی */}
            <Card
              size="small"
              title="اطلاعات اصلی"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    کد پرسنلی
                  </Text>
                  <div>
                    <Text strong>
                      {
                        selectedEmployee.personnel_code
                      }
                    </Text>
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    نام و نام خانوادگی
                  </Text>
                  <div>
                    <Text strong>
                      {
                        `${selectedEmployee.first_name} ${selectedEmployee.last_name}`
                      }
                    </Text>
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    کد ملی
                  </Text>
                  <div>
                    <Text strong>
                      {
                        selectedEmployee.national_id
                      }
                    </Text>
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    شماره شناسنامه
                  </Text>
                  <div>
                    {
                      displayValue(
                        selectedEmployee.birth_certificate_number,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    نام پدر
                  </Text>
                  <div>
                    {
                      displayValue(
                        selectedEmployee.father_name,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    جنسیت
                  </Text>
                  <div>
                    {
                      getGenderLabel(
                        selectedEmployee.gender,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    وضعیت تأهل
                  </Text>
                  <div>
                    {
                      getMaritalStatusLabel(
                        selectedEmployee.marital_status,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    تعداد فرزندان
                  </Text>
                  <div>
                    {
                      selectedEmployee.child_count
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    وضعیت
                  </Text>
                  <div>
                    {selectedEmployee.is_active ? (
                      <Tag color="success">
                        فعال
                      </Tag>
                    ) : (
                      <Tag color="error">
                        غیرفعال
                      </Tag>
                    )}
                  </div>
                </Col>
              </Row>
            </Card>

            {/* اطلاعات سازمانی */}
            <Card
              size="small"
              title="اطلاعات سازمانی"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    گروه کارکنان
                  </Text>
                  <div>
                    {
                      getEmployeeGroupLabel(
                        selectedEmployee.employee_group,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    واحد / دپارتمان
                  </Text>
                  <div>
                    {
                      selectedEmployee.department ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    عنوان شغلی
                  </Text>
                  <div>
                    {
                      selectedEmployee.job_title ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    سمت سازمانی
                  </Text>
                  <div>
                    {
                      selectedEmployee
                        .position_detail
                        ?.title || "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    کد سمت
                  </Text>
                  <div>
                    {
                      selectedEmployee
                        .position_detail
                        ?.code || "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    واحد سازمانی
                  </Text>
                  <div>
                    {
                      selectedEmployee
                        .position_detail
                        ?.organization_unit
                        ?.name || "—"
                    }
                  </div>
                </Col>
              </Row>
            </Card>

            {/* تحصیلات و نظام وظیفه */}
            <Card
              size="small"
              title="تحصیلات و نظام وظیفه"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    آخرین مدرک تحصیلی
                  </Text>
                  <div>
                    {
                      selectedEmployee.education_level ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    رشته تحصیلی
                  </Text>
                  <div>
                    {
                      selectedEmployee.field_of_study ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    شماره دانشجویی
                  </Text>
                  <div>
                    {
                      displayValue(
                        selectedEmployee.student_number,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    وضعیت نظام وظیفه
                  </Text>
                  <div>
                    {
                      getMilitaryStatusLabel(
                        selectedEmployee.military_status,
                      )
                    }
                  </div>
                </Col>
              </Row>
            </Card>

            {/* اطلاعات تماس و سکونت */}
            <Card
              size="small"
              title="اطلاعات تماس و سکونت"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    تلفن ثابت
                  </Text>
                  <div>
                    {
                      selectedEmployee.landline_phone ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    منطقه سکونت
                  </Text>
                  <div>
                    {
                      selectedEmployee.residence_area ||
                      "—"
                    }
                  </div>
                </Col>

                <Col span={24}>
                  <Text type="secondary">
                    آدرس
                  </Text>
                  <div>
                    {
                      selectedEmployee.address ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12}>
                  <Text type="secondary">
                    وضعیت تردد
                  </Text>
                  <div>
                    {
                      getTransportationStatusLabel(
                        selectedEmployee.transportation_status,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12}>
                  <Text type="secondary">
                    توضیحات سرویس
                  </Text>
                  <div>
                    {
                      selectedEmployee
                        .transportation_description ||
                      "—"
                    }
                  </div>
                </Col>
              </Row>
            </Card>

            {/* اطلاعات قرارداد و بیمه */}
            <Card
              size="small"
              title="اطلاعات قرارداد و بیمه"
            >
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    عنوان قرارداد
                  </Text>
                  <div>
                    {
                      selectedEmployee.contract_title ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    سمت درج‌شده در قرارداد
                  </Text>
                  <div>
                    {
                      selectedEmployee.contract_position ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    شماره بیمه
                  </Text>
                  <div>
                    {
                      selectedEmployee.insurance_number ||
                      "—"
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    تاریخ شروع به کار
                  </Text>
                  <div>
                    {
                      formatJalaliDate(
                        selectedEmployee.start_date,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    تاریخ بیمه
                  </Text>
                  <div>
                    {
                      formatJalaliDate(
                        selectedEmployee.insurance_date,
                      )
                    }
                  </div>
                </Col>

                <Col xs={24} sm={12} md={8}>
                  <Text type="secondary">
                    تاریخ تولد
                  </Text>
                  <div>
                    {
                      formatJalaliDate(
                        selectedEmployee.birth_date,
                      )
                    }
                  </div>
                </Col>
              </Row>
            </Card>

            {/* توضیحات */}
            <Card
              size="small"
              title="توضیحات"
            >
              <Text>
                {
                  selectedEmployee.notes ||
                  "توضیحاتی ثبت نشده است."
                }
              </Text>
            </Card>
          </Space>
        ) : null}
      </Modal>

      {/* Create / Edit Employee Modal */}
      <Modal
        title={
          editingEmployee
            ? "ویرایش اطلاعات کارمند"
            : "افزودن کارمند جدید"
        }
        open={modalOpen}
        onCancel={
          handleCloseCreate
        }
        width={900}
        centered
        destroyOnClose
        maskClosable={
          !saving
        }
        footer={[
          <Button
            key="cancel"
            onClick={
              handleCloseCreate
            }
            disabled={saving}
          >
            انصراف
          </Button>,

          <Button
            key="submit"
            type="primary"
            loading={saving}
            onClick={
              handleCreate
            }
          >
            {editingEmployee
              ? "ذخیره تغییرات"
              : "ثبت کارمند"}
          </Button>,
        ]}
      >
        <Form<EmployeeFormValues>
          form={form}
          layout="vertical"
          requiredMark="optional"
          style={{
            marginTop: 20,
          }}
        >
          {/* اطلاعات اصلی */}
          <Title level={5}>
            اطلاعات اصلی
          </Title>

          <Row gutter={[16, 8]}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="کد پرسنلی"
                name="personnel_code"
                rules={[
                  {
                    required: true,
                    message:
                      "کد پرسنلی را وارد کنید.",
                  },
                ]}
              >
                <Input
                  placeholder="مثلاً 1001"
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="نام"
                name="first_name"
                rules={[
                  {
                    required: true,
                    message:
                      "نام را وارد کنید.",
                  },
                ]}
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="نام خانوادگی"
                name="last_name"
                rules={[
                  {
                    required: true,
                    message:
                      "نام خانوادگی را وارد کنید.",
                  },
                ]}
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="کد ملی"
                name="national_id"
                rules={[
                  {
                    required: true,
                    message:
                      "کد ملی را وارد کنید.",
                  },
                  {
                    len: 10,
                    message:
                      "کد ملی باید دقیقاً ۱۰ رقم باشد.",
                  },
                  {
                    pattern:
                      /^\d+$/,
                    message:
                      "کد ملی باید فقط شامل عدد باشد.",
                  },
                ]}
              >
                <Input
                  maxLength={10}
                  inputMode="numeric"
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="شماره شناسنامه"
                name="birth_certificate_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="نام پدر"
                name="father_name"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="جنسیت"
                name="gender"
                rules={[
                  {
                    required: true,
                    message:
                      "جنسیت را انتخاب کنید.",
                  },
                ]}
              >
                <Select
                  options={
                    genderOptions
                  }
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="گروه کارکنان"
                name="employee_group"
                rules={[
                  {
                    required: true,
                    message:
                      "گروه کارکنان را انتخاب کنید.",
                  },
                ]}
              >
                <Select
                  options={
                    employeeGroupOptions
                  }
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="وضعیت تأهل"
                name="marital_status"
                rules={[
                  {
                    required: true,
                    message:
                      "وضعیت تأهل را انتخاب کنید.",
                  },
                ]}
              >
                <Select
                  options={
                    maritalStatusOptions
                  }
                />
              </Form.Item>
            </Col>
          </Row>

          {/* اطلاعات سازمانی */}
          <Title
            level={5}
            style={{
              marginTop: 20,
            }}
          >
            اطلاعات سازمانی
          </Title>

          <Row gutter={[16, 8]}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="واحد / دپارتمان"
                name="department"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="عنوان شغلی"
                name="job_title"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="واحد سازمانی"
                tooltip="واحد سازمانی محل فعالیت کارمند را انتخاب کنید."
              >
                <Select
                  allowClear
                  showSearch
                  loading={
                    organizationLoading
                  }
                  placeholder="انتخاب واحد سازمانی"
                  optionFilterProp="label"
                  value={
                    selectedOrganizationUnitId
                  }
                  onChange={
                    handleOrganizationUnitChange
                  }
                  options={organizationUnits.map(
                    (unit) => ({
                      label: `${unit.name} (${unit.code})`,
                      value: unit.id,
                    }),
                  )}
                  notFoundContent={
                    organizationLoading
                      ? "در حال دریافت..."
                      : "واحد سازمانی فعالی یافت نشد"
                  }
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="سمت سازمانی"
                name="position"
                tooltip="سمت را از میان سمت‌های فعال واحد انتخاب‌شده انتخاب کنید."
              >
                <Select
                  allowClear
                  showSearch
                  loading={
                    positionLoading
                  }
                  disabled={
                    selectedOrganizationUnitId ===
                    undefined
                  }
                  placeholder={
                    selectedOrganizationUnitId ===
                    undefined
                      ? "ابتدا واحد سازمانی را انتخاب کنید"
                      : "انتخاب سمت سازمانی"
                  }
                  optionFilterProp="label"
                  options={positions.map(
                    (position) => ({
                      label: `${position.title} (${position.code})`,
                      value: position.id,
                    }),
                  )}
                  notFoundContent={
                    positionLoading
                      ? "در حال دریافت..."
                      : "سمت فعالی برای این واحد یافت نشد"
                  }
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="شماره بیمه"
                name="insurance_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="تاریخ تولد"
                name="birth_date"
                extra="فرمت: 1400-01-01"
                rules={[
                  {
                    pattern:
                      /^\d{4}-\d{2}-\d{2}$/,
                    message:
                      "تاریخ را به صورت 1400-01-01 وارد کنید.",
                  },
                ]}
              >
                <Input
                  placeholder="1400-01-01"
                  maxLength={10}
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="تاریخ شروع به کار"
                name="start_date"
                extra="فرمت: 1400-01-01"
                rules={[
                  {
                    pattern:
                      /^\d{4}-\d{2}-\d{2}$/,
                    message:
                      "تاریخ را به صورت 1400-01-01 وارد کنید.",
                  },
                ]}
              >
                <Input
                  placeholder="1400-01-01"
                  maxLength={10}
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="تاریخ بیمه"
                name="insurance_date"
                extra="فرمت: 1400-01-01"
                rules={[
                  {
                    pattern:
                      /^\d{4}-\d{2}-\d{2}$/,
                    message:
                      "تاریخ را به صورت 1400-01-01 وارد کنید.",
                  },
                ]}
              >
                <Input
                  placeholder="1400-01-01"
                  maxLength={10}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* تحصیلات و نظام وظیفه */}
          <Title
            level={5}
            style={{
              marginTop: 20,
            }}
          >
            تحصیلات و نظام وظیفه
          </Title>

          <Row gutter={[16, 8]}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="آخرین مدرک تحصیلی"
                name="education_level"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="رشته تحصیلی"
                name="field_of_study"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="شماره دانشجویی"
                name="student_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="وضعیت نظام وظیفه"
                name="military_status"
              >
                <Select
                  allowClear
                  options={
                    militaryStatusOptions
                  }
                />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="تعداد فرزندان"
                name="child_count"
              >
                <InputNumber
                  min={0}
                  max={50}
                  precision={0}
                  style={{
                    width: "100%",
                  }}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* اطلاعات تماس و سکونت */}
          <Title
            level={5}
            style={{
              marginTop: 20,
            }}
          >
            اطلاعات تماس و سکونت
          </Title>

          <Row gutter={[16, 8]}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="تلفن ثابت"
                name="landline_phone"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="منطقه سکونت"
                name="residence_area"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="وضعیت تردد"
                name="transportation_status"
              >
                <Select
                  allowClear
                  options={
                    transportationStatusOptions
                  }
                />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item
                label="آدرس"
                name="address"
              >
                <Input.TextArea
                  rows={3}
                />
              </Form.Item>
            </Col>

            <Col span={24}>
              <Form.Item
                label="توضیحات سرویس"
                name="transportation_description"
              >
                <Input.TextArea
                  rows={2}
                />
              </Form.Item>
            </Col>
          </Row>

          {/* قرارداد */}
          <Title
            level={5}
            style={{
              marginTop: 20,
            }}
          >
            اطلاعات قرارداد
          </Title>

          <Row gutter={[16, 8]}>
            <Col xs={24} md={12}>
              <Form.Item
                label="عنوان قرارداد"
                name="contract_title"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                label="سمت درج‌شده در قرارداد"
                name="contract_position"
              >
                <Input />
              </Form.Item>
            </Col>
          </Row>

          {/* توضیحات */}
          <Title
            level={5}
            style={{
              marginTop: 20,
            }}
          >
            توضیحات
          </Title>

          <Form.Item
            label="یادداشت"
            name="notes"
          >
            <Input.TextArea
              rows={3}
              placeholder="توضیحات تکمیلی..."
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}