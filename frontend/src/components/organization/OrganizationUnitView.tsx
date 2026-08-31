import {
  Button,
  Card,
  Modal,
  Space,
  Tag,
  Typography,
} from "antd"
import { EditOutlined } from "@ant-design/icons"

import type { OrganizationUnit } from "../../types/organization"

const { Text } = Typography

interface OrganizationUnitViewProps {
  unit: OrganizationUnit | null
  open: boolean
  parentName?: string
  onClose: () => void
  onEdit: (unit: OrganizationUnit) => void
}

function getUnitTypeLabel(
  unitType: OrganizationUnit["unit_type"],
): string {
  const labels: Record<
    OrganizationUnit["unit_type"],
    string
  > = {
    company: "شرکت",
    management: "مدیریت",
    deputy: "معاونت",
    department: "دپارتمان",
    unit: "واحد",
    section: "بخش",
  }

  return labels[unitType] ?? unitType
}

export default function OrganizationUnitView({
  unit,
  open,
  parentName,
  onClose,
  onEdit,
}: OrganizationUnitViewProps) {
  return (
    <Modal
      title="مشاهده واحد سازمانی"
      open={open}
      onCancel={onClose}
      footer={[
        <Button
          key="close"
          onClick={onClose}
        >
          بستن
        </Button>,

        <Button
          key="edit"
          type="primary"
          icon={<EditOutlined />}
          disabled={!unit}
          onClick={() => {
            if (unit) {
              onEdit(unit)
            }
          }}
        >
          ویرایش
        </Button>,
      ]}
      width={650}
    >
      {unit && (
        <Space
          direction="vertical"
          size="middle"
          style={{
            width: "100%",
            marginTop: 10,
          }}
        >
          <Card size="small">
            <Text strong>
              کد واحد:{" "}
            </Text>

            <Text>
              {unit.code}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              نام واحد:{" "}
            </Text>

            <Text>
              {unit.name}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              نوع واحد:{" "}
            </Text>

            <Text>
              {getUnitTypeLabel(
                unit.unit_type,
              )}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              واحد والد:{" "}
            </Text>

            <Text>
              {unit.parent
                ? parentName ??
                  unit.parent
                : "بدون واحد والد"}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              وضعیت:{" "}
            </Text>

            {unit.is_active ? (
              <Tag color="success">
                فعال
              </Tag>
            ) : (
              <Tag color="error">
                غیرفعال
              </Tag>
            )}
          </Card>

          <Card size="small">
            <Text strong>
              توضیحات:{" "}
            </Text>

            <div
              style={{
                marginTop: 8,
                whiteSpace: "pre-wrap",
              }}
            >
              {unit.description || "—"}
            </div>
          </Card>
        </Space>
      )}
    </Modal>
  )
}