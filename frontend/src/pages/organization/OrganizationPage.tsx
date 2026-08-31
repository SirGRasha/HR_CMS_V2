import {
  Alert,
  Button,
  Card,
  Form,
  Input,
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
  createOrganizationUnit,
  createPosition,
  deleteOrganizationUnit,
  deletePosition,
  getOrganizationUnit,
  getOrganizationUnits,
  getPosition,
  getPositions,
  updateOrganizationUnit,
  updatePosition,
} from "../../api/organization"

import OrganizationUnitForm from "../../components/organization/OrganizationUnitForm"
import OrganizationUnitView from "../../components/organization/OrganizationUnitView"
import PositionForm from "../../components/organization/PositionForm"
import PositionView from "../../components/organization/PositionView"

import type {
  OrganizationUnit,
  OrganizationUnitType,
  Position,
} from "../../types/organization"

const { Title, Text } = Typography

const unitTypeOptions = [
  {
    label: "شرکت",
    value: "company",
  },
  {
    label: "مدیریت",
    value: "management",
  },
  {
    label: "معاونت",
    value: "deputy",
  },
  {
    label: "دپارتمان",
    value: "department",
  },
  {
    label: "واحد",
    value: "unit",
  },
  {
    label: "بخش",
    value: "section",
  },
]

function getUnitTypeLabel(
  value: OrganizationUnitType,
): string {
  return (
    unitTypeOptions.find(
      (item) => item.value === value,
    )?.label ?? value
  )
}

function getApiErrorMessage(
  err: unknown,
): string {
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
      const data =
        error.data as Record<
          string,
          unknown
        >

      const messages: string[] = []

      const fieldLabels: Record<
        string,
        string
      > = {
        code: "کد",
        name: "نام واحد",
        title: "عنوان پست",
        unit_type: "نوع واحد",
        parent: "واحد والد",
        organization_unit:
          "واحد سازمانی",
        is_active: "وضعیت",
        description: "توضیحات",
        detail: "جزئیات",
        non_field_errors:
          "خطا",
      }

      Object.entries(data).forEach(
        ([field, value]) => {
          const label =
            fieldLabels[field] ?? field

          if (Array.isArray(value)) {
            value.forEach((item) => {
              messages.push(
                `${label}: ${String(item)}`,
              )
            })
          } else if (
            value !== undefined &&
            value !== null
          ) {
            messages.push(
              `${label}: ${String(value)}`,
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

type UnitFormValues = {
  code: string
  name: string
  unit_type: OrganizationUnitType
  parent: number | null
  is_active: boolean
  description: string
}

type PositionFormValues = {
  code: string
  title: string
  organization_unit: number
  is_active: boolean
  description: string
}

export default function OrganizationPage() {
  const [unitForm] =
    Form.useForm<UnitFormValues>()

  const [positionForm] =
    Form.useForm<PositionFormValues>()

  const [units, setUnits] =
    useState<OrganizationUnit[]>([])

  const [positions, setPositions] =
    useState<Position[]>([])

  const [loading, setLoading] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [error, setError] =
    useState<string | null>(null)

  /* =========================
     Unit Filters
     ========================= */

  const [unitSearch, setUnitSearch] =
    useState("")

  const [
    unitActiveFilter,
    setUnitActiveFilter,
  ] = useState<boolean | undefined>(
    undefined,
  )

  const [
    unitTypeFilter,
    setUnitTypeFilter,
  ] = useState<
    OrganizationUnitType | undefined
  >(undefined)

  /* =========================
     Position Filters
     ========================= */

  const [
    positionSearch,
    setPositionSearch,
  ] = useState("")

  const [
    positionActiveFilter,
    setPositionActiveFilter,
  ] = useState<boolean | undefined>(
    undefined,
  )

  const [
    positionUnitFilter,
    setPositionUnitFilter,
  ] = useState<number | undefined>(
    undefined,
  )

  /* =========================
     Unit Modals
     ========================= */

  const [
    unitModalOpen,
    setUnitModalOpen,
  ] = useState(false)

  const [
    editingUnit,
    setEditingUnit,
  ] = useState<OrganizationUnit | null>(
    null,
  )

  const [
    viewingUnit,
    setViewingUnit,
  ] = useState<OrganizationUnit | null>(
    null,
  )

  /* =========================
     Position Modals
     ========================= */

  const [
    positionModalOpen,
    setPositionModalOpen,
  ] = useState(false)

  const [
    editingPosition,
    setEditingPosition,
  ] = useState<Position | null>(
    null,
  )

  const [
    viewingPosition,
    setViewingPosition,
  ] = useState<Position | null>(
    null,
  )

  /* =========================
     Load Data
     ========================= */

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [
        unitsResponse,
        positionsResponse,
      ] = await Promise.all([
        getOrganizationUnits(),
        getPositions(),
      ])

      setUnits(unitsResponse)
      setPositions(positionsResponse)
    } catch (err) {
      console.error(
        "LOAD ORGANIZATION ERROR:",
        err,
      )

      setError(
        `خطا در دریافت ساختار سازمانی: ${getApiErrorMessage(
          err,
        )}`,
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  /* =========================
     Maps
     ========================= */

  const unitMap = useMemo(() => {
    return new Map(
      units.map((unit) => [
        unit.id,
        unit,
      ]),
    )
  }, [units])

  /* =========================
     Filtered Units
     ========================= */

  const filteredUnits =
    useMemo(() => {
      const query =
        unitSearch
          .trim()
          .toLowerCase()

      return units.filter((unit) => {
        if (
          unitActiveFilter !==
            undefined &&
          unit.is_active !==
            unitActiveFilter
        ) {
          return false
        }

        if (
          unitTypeFilter &&
          unit.unit_type !==
            unitTypeFilter
        ) {
          return false
        }

        if (!query) {
          return true
        }

        return [
          unit.code,
          unit.name,
          unit.description,
        ].some((value) =>
          String(value ?? "")
            .toLowerCase()
            .includes(query),
        )
      })
    }, [
      units,
      unitSearch,
      unitActiveFilter,
      unitTypeFilter,
    ])

  /* =========================
     Filtered Positions
     ========================= */

  const filteredPositions =
    useMemo(() => {
      const query =
        positionSearch
          .trim()
          .toLowerCase()

      return positions.filter(
        (position) => {
          if (
            positionActiveFilter !==
              undefined &&
            position.is_active !==
              positionActiveFilter
          ) {
            return false
          }

          if (
            positionUnitFilter !==
              undefined &&
            position.organization_unit !==
              positionUnitFilter
          ) {
            return false
          }

          if (!query) {
            return true
          }

          return [
            position.code,
            position.title,
            position.description,
          ].some((value) =>
            String(value ?? "")
              .toLowerCase()
              .includes(query),
          )
        },
      )
    }, [
      positions,
      positionSearch,
      positionActiveFilter,
      positionUnitFilter,
    ])

  const openCreateUnit = () => {
    setEditingUnit(null)
    setViewingUnit(null)

    unitForm.resetFields()

    unitForm.setFieldsValue({
      is_active: true,
      parent: null,
    })

    setUnitModalOpen(true)
  }

  const openEditUnit = async (
    unit: OrganizationUnit,
  ) => {
    try {
      setSaving(true)

      const latest =
        await getOrganizationUnit(
          unit.id,
        )

      setEditingUnit(latest)
      setViewingUnit(null)

      unitForm.setFieldsValue({
        code: latest.code,
        name: latest.name,
        unit_type:
          latest.unit_type,
        parent: latest.parent,
        is_active:
          latest.is_active,
        description:
          latest.description,
      })

      setUnitModalOpen(true)
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const openViewUnit = async (
    unit: OrganizationUnit,
  ) => {
    try {
      setSaving(true)

      const latest =
        await getOrganizationUnit(
          unit.id,
        )

      setViewingUnit(latest)
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const closeUnitModal = () => {
    if (saving) {
      return
    }

    setUnitModalOpen(false)
    setEditingUnit(null)
    unitForm.resetFields()
  }

  const handleSaveUnit = async () => {
    try {
      const values =
        await unitForm.validateFields()

      setSaving(true)

      const payload = {
        code: values.code.trim(),
        name: values.name.trim(),
        unit_type:
          values.unit_type,
        parent:
          values.parent ?? null,
        is_active:
          values.is_active ?? true,
        description:
          values.description?.trim() ?? "",
      }

      if (editingUnit) {
        await updateOrganizationUnit(
          editingUnit.id,
          payload,
        )

        message.success(
          "واحد سازمانی با موفقیت بروزرسانی شد.",
        )
      } else {
        await createOrganizationUnit(
          payload,
        )

        message.success(
          "واحد سازمانی با موفقیت ایجاد شد.",
        )
      }

      setUnitModalOpen(false)
      setEditingUnit(null)
      unitForm.resetFields()

      await loadData()
    } catch (err) {
      if (
        err &&
        typeof err === "object" &&
        "errorFields" in err
      ) {
        return
      }

      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteUnit = async (
    unit: OrganizationUnit,
  ) => {
    try {
      setSaving(true)

      await deleteOrganizationUnit(
        unit.id,
      )

      message.success(
        "واحد سازمانی با موفقیت حذف شد.",
      )

      await loadData()
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  /* =========================
     Position CRUD
     ========================= */

  const openCreatePosition = () => {
    setEditingPosition(null)
    setViewingPosition(null)

    positionForm.resetFields()

    positionForm.setFieldsValue({
      is_active: true,
      ...(positionUnitFilter !==
      undefined
        ? {
            organization_unit:
              positionUnitFilter,
          }
        : {}),
    })

    setPositionModalOpen(true)
  }

  const openEditPosition = async (
    position: Position,
  ) => {
    try {
      setSaving(true)

      const latest =
        await getPosition(
          position.id,
        )

      setEditingPosition(latest)
      setViewingPosition(null)

      positionForm.setFieldsValue({
        code: latest.code,
        title: latest.title,
        organization_unit:
          latest.organization_unit,
        is_active:
          latest.is_active,
        description:
          latest.description,
      })

      setPositionModalOpen(true)
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const openViewPosition = async (
    position: Position,
  ) => {
    try {
      setSaving(true)

      const latest =
        await getPosition(
          position.id,
        )

      setViewingPosition(latest)
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const closePositionModal = () => {
    if (saving) {
      return
    }

    setPositionModalOpen(false)
    setEditingPosition(null)
    positionForm.resetFields()
  }

  const handleSavePosition = async () => {
    try {
      const values =
        await positionForm.validateFields()

      setSaving(true)

      const payload = {
        code: values.code.trim(),
        title: values.title.trim(),
        organization_unit:
          values.organization_unit,
        is_active:
          values.is_active ?? true,
        description:
          values.description?.trim() ?? "",
      }

      if (editingPosition) {
        await updatePosition(
          editingPosition.id,
          payload,
        )

        message.success(
          "پست سازمانی با موفقیت بروزرسانی شد.",
        )
      } else {
        await createPosition(
          payload,
        )

        message.success(
          "پست سازمانی با موفقیت ایجاد شد.",
        )
      }

      setPositionModalOpen(false)
      setEditingPosition(null)
      positionForm.resetFields()

      await loadData()
    } catch (err) {
      if (
        err &&
        typeof err === "object" &&
        "errorFields" in err
      ) {
        return
      }

      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDeletePosition = async (
    position: Position,
  ) => {
    try {
      setSaving(true)

      await deletePosition(
        position.id,
      )

      message.success(
        "پست سازمانی با موفقیت حذف شد.",
      )

      await loadData()
    } catch (err) {
      message.error(
        getApiErrorMessage(err),
      )
    } finally {
      setSaving(false)
    }
  }

  /* =========================
     Unit Columns
     ========================= */

  const unitColumns: ColumnsType<OrganizationUnit> =
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
        title: "کد واحد",
        dataIndex: "code",
        key: "code",
      },
      {
        title: "نام واحد",
        dataIndex: "name",
        key: "name",
      },
      {
        title: "نوع واحد",
        key: "unit_type",
        render: (_, record) =>
          getUnitTypeLabel(
            record.unit_type,
          ),
      },
      {
        title: "واحد والد",
        key: "parent",
        render: (_, record) => {
          if (!record.parent) {
            return "—"
          }

          return (
            unitMap.get(
              record.parent,
            )?.name ?? record.parent
          )
        },
      },
      {
        title: "وضعیت",
        dataIndex: "is_active",
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
        title: "عملیات",
        key: "actions",
        width: 170,
        align: "center",
        render: (_, record) => (
          <Space size="small">
            <Button
              type="text"
              icon={<EyeOutlined />}
              title="مشاهده"
              loading={
                saving &&
                viewingUnit?.id ===
                  record.id
              }
              onClick={() =>
                openViewUnit(record)
              }
            />

            <Button
              type="text"
              icon={<EditOutlined />}
              title="ویرایش"
              onClick={() =>
                openEditUnit(record)
              }
            />

            <Popconfirm
              title="حذف واحد سازمانی"
              description={`آیا از حذف «${record.name}» مطمئن هستید؟`}
              okText="بله، حذف شود"
              cancelText="انصراف"
              okButtonProps={{
                danger: true,
              }}
              onConfirm={() =>
                handleDeleteUnit(
                  record,
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

  /* =========================
     Position Columns
     ========================= */

  const positionColumns: ColumnsType<Position> =
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
        title: "کد پست",
        dataIndex: "code",
        key: "code",
      },
      {
        title: "عنوان پست",
        dataIndex: "title",
        key: "title",
      },
      {
        title: "واحد سازمانی",
        key: "organization_unit",
        render: (_, record) =>
          unitMap.get(
            record.organization_unit,
          )?.name ??
          record.organization_unit,
      },
      {
        title: "وضعیت",
        dataIndex: "is_active",
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
        title: "عملیات",
        key: "actions",
        width: 170,
        align: "center",
        render: (_, record) => (
          <Space size="small">
            <Button
              type="text"
              icon={<EyeOutlined />}
              title="مشاهده"
              loading={
                saving &&
                viewingPosition?.id ===
                  record.id
              }
              onClick={() =>
                openViewPosition(
                  record,
                )
              }
            />

            <Button
              type="text"
              icon={<EditOutlined />}
              title="ویرایش"
              onClick={() =>
                openEditPosition(
                  record,
                )
              }
            />

            <Popconfirm
              title="حذف پست سازمانی"
              description={`آیا از حذف «${record.title}» مطمئن هستید؟`}
              okText="بله، حذف شود"
              cancelText="انصراف"
              okButtonProps={{
                danger: true,
              }}
              onConfirm={() =>
                handleDeletePosition(
                  record,
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
          {/* =========================
              Header
             ========================= */}

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
                ساختار سازمانی
              </Title>

              <Text type="secondary">
                مدیریت واحدها و پست‌های
                سازمانی
              </Text>
            </div>

            <Space>
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
              defaultActiveKey="units"
              items={[
                /* =========================
                   Units Tab
                   ========================= */

                {
                  key: "units",
                  label:
                    "واحدهای سازمانی",
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
                          <Space wrap>
                            <Input
                              allowClear
                              prefix={
                                <SearchOutlined />
                              }
                              placeholder="جستجو در واحدها..."
                              value={
                                unitSearch
                              }
                              onChange={(
                                event,
                              ) =>
                                setUnitSearch(
                                  event
                                    .target
                                    .value,
                                )
                              }
                              style={{
                                width: 280,
                              }}
                            />

                            <Select
                              allowClear
                              placeholder="نوع واحد"
                              value={
                                unitTypeFilter
                              }
                              onChange={
                                setUnitTypeFilter
                              }
                              options={
                                unitTypeOptions
                              }
                              style={{
                                width: 170,
                              }}
                            />

                            <Select
                              allowClear
                              placeholder="وضعیت"
                              value={
                                unitActiveFilter
                              }
                              onChange={
                                setUnitActiveFilter
                              }
                              options={[
                                {
                                  label:
                                    "فعال",
                                  value:
                                    true,
                                },
                                {
                                  label:
                                    "غیرفعال",
                                  value:
                                    false,
                                },
                              ]}
                              style={{
                                width: 150,
                              }}
                            />
                          </Space>

                          <Button
                            type="primary"
                            icon={
                              <PlusOutlined />
                            }
                            onClick={
                              openCreateUnit
                            }
                          >
                            افزودن واحد
                          </Button>
                        </div>
                      </Card>

                      <Table<OrganizationUnit>
                        rowKey="id"
                        columns={
                          unitColumns
                        }
                        dataSource={
                          filteredUnits
                        }
                        pagination={{
                          pageSize: 10,
                          showSizeChanger:
                            true,
                          showTotal: (
                            total,
                          ) =>
                            `تعداد ${total} واحد`,
                        }}
                        scroll={{
                          x: 1050,
                        }}
                        locale={{
                          emptyText:
                            "هیچ واحد سازمانی یافت نشد",
                        }}
                      />
                    </Space>
                  ),
                },

                /* =========================
                   Positions Tab
                   ========================= */

                {
                  key: "positions",
                  label:
                    "پست‌های سازمانی",
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
                          <Space wrap>
                            <Input
                              allowClear
                              prefix={
                                <SearchOutlined />
                              }
                              placeholder="جستجو در پست‌ها..."
                              value={
                                positionSearch
                              }
                              onChange={(
                                event,
                              ) =>
                                setPositionSearch(
                                  event
                                    .target
                                    .value,
                                )
                              }
                              style={{
                                width: 280,
                              }}
                            />

                            <Select
                              allowClear
                              showSearch
                              optionFilterProp="label"
                              placeholder="واحد سازمانی"
                              value={
                                positionUnitFilter
                              }
                              onChange={
                                setPositionUnitFilter
                              }
                              options={units.map(
                                (
                                  unit,
                                ) => ({
                                  label:
                                    `${unit.code} - ${unit.name}`,
                                  value:
                                    unit.id,
                                }),
                              )}
                              style={{
                                width: 240,
                              }}
                            />

                            <Select
                              allowClear
                              placeholder="وضعیت"
                              value={
                                positionActiveFilter
                              }
                              onChange={
                                setPositionActiveFilter
                              }
                              options={[
                                {
                                  label:
                                    "فعال",
                                  value:
                                    true,
                                },
                                {
                                  label:
                                    "غیرفعال",
                                  value:
                                    false,
                                },
                              ]}
                              style={{
                                width: 150,
                              }}
                            />
                          </Space>

                          <Button
                            type="primary"
                            icon={
                              <PlusOutlined />
                            }
                            onClick={
                              openCreatePosition
                            }
                          >
                            افزودن پست
                          </Button>
                        </div>
                      </Card>

                      <Table<Position>
                        rowKey="id"
                        columns={
                          positionColumns
                        }
                        dataSource={
                          filteredPositions
                        }
                        pagination={{
                          pageSize: 10,
                          showSizeChanger:
                            true,
                          showTotal: (
                            total,
                          ) =>
                            `تعداد ${total} پست`,
                        }}
                        scroll={{
                          x: 900,
                        }}
                        locale={{
                          emptyText:
                            "هیچ پست سازمانی یافت نشد",
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

      {/* =========================================================
          Unit Create / Edit Modal
          ========================================================= */}

      <Modal
        title={
          editingUnit
            ? "ویرایش واحد سازمانی"
            : "افزودن واحد سازمانی"
        }
        open={unitModalOpen}
        onCancel={closeUnitModal}
        onOk={handleSaveUnit}
        okText={
          editingUnit
            ? "ذخیره تغییرات"
            : "ایجاد واحد"
        }
        cancelText="انصراف"
        confirmLoading={saving}
        destroyOnHidden
        width={650}
      >
        <OrganizationUnitForm
          form={unitForm}
          units={units}
          editingUnit={editingUnit}
        />
      </Modal>

      {/* =========================================================
          Unit View Modal
          ========================================================= */}

      <OrganizationUnitView
        unit={viewingUnit}
        open={viewingUnit !== null}
        parentName={
          viewingUnit?.parent
            ? unitMap.get(
                viewingUnit.parent,
              )?.name
            : undefined
        }
        onClose={() =>
          setViewingUnit(null)
        }
        onEdit={(unit) => {
          setViewingUnit(null)
          openEditUnit(unit)
        }}
      />

      {/* =========================================================
          Position Create / Edit Modal
          ========================================================= */}

      <Modal
        title={
          editingPosition
            ? "ویرایش پست سازمانی"
            : "افزودن پست سازمانی"
        }
        open={positionModalOpen}
        onCancel={
          closePositionModal
        }
        onOk={
          handleSavePosition
        }
        okText={
          editingPosition
            ? "ذخیره تغییرات"
            : "ایجاد پست"
        }
        cancelText="انصراف"
        confirmLoading={saving}
        destroyOnHidden
        width={650}
      >
        <PositionForm
          form={positionForm}
          units={units}
        />
      </Modal>

      {/* =========================================================
          Position View Modal
          ========================================================= */}

      <PositionView
        position={viewingPosition}
        open={
          viewingPosition !== null
        }
        units={units}
        onClose={() =>
          setViewingPosition(null)
        }
        onEdit={(position) => {
          setViewingPosition(null)
          openEditPosition(position)
        }}
      />
    </div>
  )
}