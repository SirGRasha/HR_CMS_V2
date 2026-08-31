import {
  Button,
  Card,
  Modal,
  Space,
  Tag,
  Typography,
} from "antd"
import { EditOutlined } from "@ant-design/icons"

import type {
  OrganizationUnit,
  Position,
} from "../../types/organization"

const { Text } = Typography

interface PositionViewProps {
  position: Position | null
  open: boolean
  units: OrganizationUnit[]
  onClose: () => void
  onEdit: (position: Position) => void
}

function getOrganizationUnitName(
  position: Position,
  units: OrganizationUnit[],
): string | number {
  return (
    units.find(
      (unit) =>
        unit.id === position.organization_unit,
    )?.name ??
    position.organization_unit
  )
}

export default function PositionView({
  position,
  open,
  units,
  onClose,
  onEdit,
}: PositionViewProps) {
  return (
    <Modal
      title="مشاهده پست سازمانی"
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
          disabled={!position}
          onClick={() => {
            if (position) {
              onEdit(position)
            }
          }}
        >
          ویرایش
        </Button>,
      ]}
      width={650}
    >
      {position && (
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
              کد پست:{" "}
            </Text>

            <Text>
              {position.code}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              عنوان پست:{" "}
            </Text>

            <Text>
              {position.title}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              واحد سازمانی:{" "}
            </Text>

            <Text>
              {getOrganizationUnitName(
                position,
                units,
              )}
            </Text>
          </Card>

          <Card size="small">
            <Text strong>
              وضعیت:{" "}
            </Text>

            {position.is_active ? (
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
              {position.description ||
                "—"}
            </div>
          </Card>
        </Space>
      )}
    </Modal>
  )
}