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
} from "@ant-design/icons"
import { useEffect, useMemo, useState } from "react"

import {
  createEmployee,
  getEmployees,
} from "../../api/employees"

import type {
  Employee,
} from "../../types/employee"

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
      const data = error.data as Record<
        string,
        unknown
      >

      const messages: string[] = []

      Object.entries(data).forEach(
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

  useEffect(() => {
    loadEmployees()
  }, [activeFilter])

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

  const handleOpenCreate = () => {
    form.resetFields()

    form.setFieldsValue({
      child_count: 0,
      gender: "male",
      employee_group: "administrative",
      marital_status: "single",
    })

    setModalOpen(true)
  }

  const handleCloseCreate = () => {
    if (saving) {
      return
    }

    setModalOpen(false)
    form.resetFields()
  }

  const handleCreate = async () => {
    try {
      const values =
        await form.validateFields()

      setSaving(true)

      await createEmployee({
        personnel_code:
          values.personnel_code,

        first_name:
          values.first_name,

        last_name:
          values.last_name,

        national_id:
          values.national_id,

        birth_certificate_number:
          values.birth_certificate_number ??
          "",

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
          values.transportation_status ??
          "",

        transportation_description:
          values.transportation_description ??
          "",

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

        is_active: true,
      })

      message.success(
        "کارمند با موفقیت ثبت شد.",
      )

      setModalOpen(false)
      form.resetFields()

      await loadEmployees()
    } catch (err) {
      console.error(
        "CREATE EMPLOYEE ERROR:",
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
        `ثبت کارمند با خطا مواجه شد: ${errorMessage}`,
        6,
      )
    } finally {
      setSaving(false)
    }
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
          "گروه کارکنان",
        key: "employee_group",
        render: (
          _,
          record,
        ) =>
          getEmployeeGroupLabel(
            record.employee_group,
          ),
      },

      {
        title:
          "عنوان شغلی",
        dataIndex:
          "job_title",
        key: "job_title",
        render: (
          value: string,
        ) =>
          value || "—",
      },

      {
        title:
          "سمت سازمانی",
        key: "position",
        render: (
          _,
          record,
        ) =>
          record.position_detail
            ?.title ??
          "—",
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
        render: () => (
          <Button
            type="link"
            icon={
              <EyeOutlined />
            }
          >
            مشاهده
          </Button>
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
                مدیریت اطلاعات کارکنان سازمان
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
                x: 1000,
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

      {/* Create Employee Modal */}
      <Modal
        title="افزودن کارمند جدید"
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
            ثبت کارمند
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

          <Row
            gutter={[
              16,
              8,
            ]}
          >
            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="شماره شناسنامه"
                name="birth_certificate_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="نام پدر"
                name="father_name"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

          <Row
            gutter={[
              16,
              8,
            ]}
          >
            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="واحد / دپارتمان"
                name="department"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="عنوان شغلی"
                name="job_title"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="شناسه سمت سازمانی"
                name="position"
                tooltip="در این مرحله شناسه عددی سمت سازمانی را وارد کنید."
                rules={[
                  {
                    type: "number",
                    min: 1,
                    message:
                      "شناسه سمت سازمانی باید یک عدد معتبر بزرگ‌تر از صفر باشد.",
                  },
                ]}
              >
                <InputNumber
                  style={{
                    width: "100%",
                  }}
                  min={1}
                  precision={0}
                  placeholder="مثلاً 1"
                />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="شماره بیمه"
                name="insurance_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

          <Row
            gutter={[
              16,
              8,
            ]}
          >
            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="آخرین مدرک تحصیلی"
                name="education_level"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="رشته تحصیلی"
                name="field_of_study"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="شماره دانشجویی"
                name="student_number"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

          <Row
            gutter={[
              16,
              8,
            ]}
          >
            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="تلفن ثابت"
                name="landline_phone"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
              <Form.Item
                label="منطقه سکونت"
                name="residence_area"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              sm={12}
              md={8}
            >
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

          <Row
            gutter={[
              16,
              8,
            ]}
          >
            <Col
              xs={24}
              md={12}
            >
              <Form.Item
                label="عنوان قرارداد"
                name="contract_title"
              >
                <Input />
              </Form.Item>
            </Col>

            <Col
              xs={24}
              md={12}
            >
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