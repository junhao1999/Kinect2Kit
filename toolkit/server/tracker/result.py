class Result(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.perspectives_dict = dict()

    def get_timestamp(self):
        return self.timestamp

    def add_perspective(self, perspective):
        self.perspectives_dict[perspective.get_name()] = perspective

    def get_perspectives(self):
        return self.perspectives_dict

    def to_dict(self):
        result_vars = dict()
        result_vars["Timestamp"] = self.timestamp
        result_vars["Perspectives"] = dict()

        for perspective in self.perspectives_dict.itervalues():
            perspective_vars = dict()
            perspective_vars["KinectName"] = perspective.get_name()
            perspective_vars["KinectIPAddress"] = perspective.get_addr()
            perspective_vars["People"] = list()

            for person in perspective.get_people():
                person_vars = dict()
                person_vars["Id"] = person.get_id()
                person_vars["Skeletons"] = person.get_skeletons()
                person_vars["AverageSkeleton"] = person.get_average_skeleton()
                perspective_vars["People"].append(person_vars)

                # for s in person_vars["Skeletons"].itervalues():
                #     print "result to dict: skel head", s["Joints"]["Head"]["CameraSpacePoint"]
                # print "result to dict: avg head", person_vars["AverageSkeleton"]["Head"]["CameraSpacePoint"]

            result_vars["Perspectives"][perspective_vars["KinectName"]] = perspective_vars

        return result_vars


def create_result(*args):
    return Result(*args)


class Perspective(object):
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.people_list = list()

    def get_name(self):
        return self.name

    def get_addr(self):
        return self.addr

    def add_person(self, person):
        self.people_list.append(person)

    def get_people(self):
        return self.people_list


def create_perspective(*args):
    return Perspective(*args)


class Person(object):
    def __init__(self, id):
        self.id = id
        self.skeletons_dict = dict()
        self.average_skeleton = None

    def get_id(self):
        return self.id

    def add_skeleton(self, is_native, kinect_name, kinect_addr, joints_dict):
        self.skeletons_dict[kinect_name] = {
            "IsNative": str(is_native),
            "KinectName": kinect_name,
            "KinectIPAddress": kinect_addr,
            "Joints": joints_dict
        }

    def get_skeletons(self):
        return self.skeletons_dict

    def calculate_average_skeleton(self):
        # joint type as key and tuple of total joint position and number of kinects as value
        # total joint position = sum of tracked joint positions, in terms of x, y, and z
        total_joints_positions = dict()

        for skeleton in self.skeletons_dict.itervalues():

            # print "skel head", skeleton["Joints"]["Head"]["CameraSpacePoint"]

            for joint_type, joint in skeleton["Joints"].iteritems():
                # value of TrackingState.Tracked is 2
                if joint["TrackingState"] != 2:
                    continue

                if joint_type not in total_joints_positions:
                    # copy joint
                    new_total_joint_pos = dict()
                    new_total_joint_pos["X"] = joint["CameraSpacePoint"]["X"]
                    new_total_joint_pos["Y"] = joint["CameraSpacePoint"]["Y"]
                    new_total_joint_pos["Z"] = joint["CameraSpacePoint"]["Z"]
                    total_joints_positions[joint_type] = (new_total_joint_pos, 1)
                else:
                    total_joint_pos = total_joints_positions[joint_type][0]
                    total_joint_pos["X"] += joint["CameraSpacePoint"]["X"]
                    total_joint_pos["Y"] += joint["CameraSpacePoint"]["Y"]
                    total_joint_pos["Z"] += joint["CameraSpacePoint"]["Z"]
                    kinects_count = total_joints_positions[joint_type][1]
                    kinects_count += 1
                    total_joints_positions[joint_type] = (total_joint_pos, kinects_count)

        average_skeleton = dict()
        for joint_type, (total_position, kinects_count) in total_joints_positions.iteritems():
            average_joint = dict()
            average_joint["JointType"] = joint_type
            average_joint["TrackingState"] = 2
            average_joint["CameraSpacePoint"] = dict()
            average_joint["CameraSpacePoint"]["X"] = total_position["X"] / float(kinects_count)
            average_joint["CameraSpacePoint"]["Y"] = total_position["Y"] / float(kinects_count)
            average_joint["CameraSpacePoint"]["Z"] = total_position["Z"] / float(kinects_count)
            average_skeleton[joint_type] = average_joint
            #
            # if joint_type == "Head":
            #     print "avg head total pos", total_position
            #     print "avg head count", kinects_count
            #     print "avg head pos", average_joint

        self.average_skeleton = average_skeleton

    def get_average_skeleton(self):
        return self.average_skeleton


def create_person(*args):
    return Person(*args)
